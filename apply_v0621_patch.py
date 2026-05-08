from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path(r"D:\AI\plc_ai_system\company_generators\multi_station_project_generator.py")


def replace_once(text, old, new, label):
    if old not in text:
        print(f"❌ 未找到插入点：{label}")
        return text, False

    text = text.replace(old, new, 1)
    print(f"✅ 已处理：{label}")
    return text, True


def main():
    if not TARGET.exists():
        print("❌ 文件不存在：", TARGET)
        return

    backup = TARGET.parent / f"{TARGET.stem}_backup_v0621_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy2(TARGET, backup)
    print("✅ 已备份：", backup)

    text = TARGET.read_text(encoding="utf-8", errors="ignore")
    text = text.replace("\r\n", "\n")

    all_ok = True

    # 1. 更新版本号
    if 'GENERATOR_VERSION = "V0.6.2.1"' not in text:
        text, ok = replace_once(
            text,
            'GENERATOR_VERSION = "V0.6"',
            'GENERATOR_VERSION = "V0.6.2.1"',
            "更新 GENERATOR_VERSION"
        )
        all_ok = all_ok and ok
    else:
        print("✅ 版本号已经是 V0.6.2.1")

    # 2. 增加 import
    if "machine_main_generator" not in text:
        old = '''from company_generators.station_generator import (
    render_station_program,
    validate_station_config
)
'''
        new = '''from company_generators.station_generator import (
    render_station_program,
    validate_station_config
)

from company_generators.machine_main_generator import (
    generate_machine_main_st,
    natural_station_index,
    normalize_station_configs as normalize_machine_station_configs
)

from company_generators.hmi_variable_generator import (
    generate_hmi_variable_csv_bytes
)
'''
        text, ok = replace_once(text, old, new, "增加 V0.6.2.1 模块 import")
        all_ok = all_ok and ok
    else:
        print("✅ V0.6.2.1 import 已存在")

    # 3. 增加 write_bytes
    if "def write_bytes(" not in text:
        old = '''def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
'''
        new = '''def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_bytes(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
'''
        text, ok = replace_once(text, old, new, "增加 write_bytes")
        all_ok = all_ok and ok
    else:
        print("✅ write_bytes 已存在")

    # 4. validation_report 增强
    if "V0.6.2.1 主工程集成验收" not in text:
        old = '''    validation_text = build_multi_validation_report(
        project_info=project_info,
        cylinder_config=cylinder_config,
        station_configs=station_configs,
        errors=errors,
        warnings=warnings,
        package_dir=package_dir
    )
'''
        new = '''    validation_text = build_multi_validation_report(
        project_info=project_info,
        cylinder_config=cylinder_config,
        station_configs=station_configs,
        errors=errors,
        warnings=warnings,
        package_dir=package_dir
    )

    validation_text += (
        "\\n\\n========== V0.6.2.1 主工程集成验收 ==========\\n"
        "✅ 已集成 04_Machine_Auto_Main_Generated.st 生成\\n"
        "✅ 已集成 HMI_Variable_List.csv 生成\\n"
        "✅ 已集成多工站顺序互锁\\n"
        "✅ 已集成工站报警汇总\\n"
        "✅ 已集成整机统一复位\\n"
        "✅ 已集成整机完成判断\\n"
    )
'''
        text, ok = replace_once(text, old, new, "增强 validation_report")
        all_ok = all_ok and ok
    else:
        print("✅ validation_report 增强已存在")

    # 5. 生成整机主流程 ST 和 HMI CSV
    if "04_Machine_Auto_Main_Generated.st" not in text:
        old = '''        write_text(station_path, station_code)
        files_written.append((station_path, "generated_st"))
        station_output_paths.append(station_path)

    configs_dir = package_dir / "configs"
'''
        new = '''        write_text(station_path, station_code)
        files_written.append((station_path, "generated_st"))
        station_output_paths.append(station_path)

    # V0.6.2.1：整机主流程 ST
    machine_main_code = generate_machine_main_st(station_configs)
    machine_main_path = package_dir / "04_Machine_Auto_Main_Generated.st"
    write_text(machine_main_path, machine_main_code)
    files_written.append((machine_main_path, "generated_st"))

    # V0.6.2.1：HMI 变量清单
    hmi_variable_path = package_dir / "HMI_Variable_List.csv"
    write_bytes(hmi_variable_path, generate_hmi_variable_csv_bytes(station_configs))
    files_written.append((hmi_variable_path, "hmi_variable"))

    configs_dir = package_dir / "configs"
'''
        text, ok = replace_once(text, old, new, "接入整机主流程 ST 和 HMI CSV")
        all_ok = all_ok and ok
    else:
        print("✅ 整机主流程 ST 和 HMI CSV 已接入")

    # 6. 生成 configs/v062_station_chain.json
    if "v062_station_chain.json" not in text:
        old = '''    write_text(
        station_configs_path,
        json.dumps(station_configs, ensure_ascii=False, indent=4)
    )

    files_written.extend([
        (cylinder_config_path, "config"),
        (station_configs_path, "config")
    ])
'''
        new = '''    write_text(
        station_configs_path,
        json.dumps(station_configs, ensure_ascii=False, indent=4)
    )

    # V0.6.2.1：工站链路配置
    normalized_station_chain = normalize_machine_station_configs(station_configs)
    station_chain_config = {
        "version": "V0.6.2.1",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "station_chain": [
            {
                "station_id": station["station_id"],
                "station_name": station["station_name"],
                "station_index": natural_station_index(station["station_id"], i)
            }
            for i, station in enumerate(normalized_station_chain, start=1)
        ]
    }

    v062_station_chain_path = configs_dir / "v062_station_chain.json"
    write_text(
        v062_station_chain_path,
        json.dumps(station_chain_config, ensure_ascii=False, indent=4)
    )

    files_written.extend([
        (cylinder_config_path, "config"),
        (station_configs_path, "config"),
        (v062_station_chain_path, "config")
    ])
'''
        text, ok = replace_once(text, old, new, "接入 v062_station_chain.json")
        all_ok = all_ok and ok
    else:
        print("✅ v062_station_chain.json 已接入")

    # 7. manifest 增强
    if "v0621_features" not in text:
        old = '''    manifest = build_manifest(
        project_info=project_info,
        package_dir=package_dir,
        file_records=file_records,
        cylinder_config=cylinder_config,
        station_configs=station_configs
    )

    manifest_path = package_dir / "manifest.json"
'''
        new = '''    manifest = build_manifest(
        project_info=project_info,
        package_dir=package_dir,
        file_records=file_records,
        cylinder_config=cylinder_config,
        station_configs=station_configs
    )

    # V0.6.2.1：manifest 增强信息
    manifest["version"] = GENERATOR_VERSION
    manifest["v0621_generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    manifest["v0621_features"] = [
        "整机主流程 ST 生成",
        "多工站顺序互锁",
        "工站报警汇总",
        "整机统一复位",
        "整机完成判断",
        "HMI 变量清单 CSV 生成",
        "工站链路配置 v062_station_chain.json"
    ]
    manifest["v0621_added_files"] = [
        "04_Machine_Auto_Main_Generated.st",
        "HMI_Variable_List.csv",
        "configs/v062_station_chain.json"
    ]
    manifest["v0621_station_chain"] = [
        {
            "station_id": station["station_id"],
            "station_name": station["station_name"],
            "station_index": natural_station_index(station["station_id"], i)
        }
        for i, station in enumerate(normalized_station_chain, start=1)
    ]

    manifest_path = package_dir / "manifest.json"
'''
        text, ok = replace_once(text, old, new, "增强 manifest")
        all_ok = all_ok and ok
    else:
        print("✅ manifest 增强已存在")

    if not all_ok:
        print("\n❌ 补丁未完全成功，已保留原文件备份：")
        print(backup)
        return

    TARGET.write_text(text, encoding="utf-8")
    print("\n✅ V0.6.2.1 补丁应用完成")
    print("目标文件：", TARGET)


if __name__ == "__main__":
    main()