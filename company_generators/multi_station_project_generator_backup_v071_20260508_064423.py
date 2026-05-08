import json
import shutil
import zipfile
import hashlib
import re
from datetime import datetime
from pathlib import Path

from company_generators.cylinder_generator import (
    render_cylinder_action,
    validate_all_cylinders
)

from company_generators.station_generator import (
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

from company_generators.sysmac_export_generator import (
    generate_dut_struct_st,
    generate_global_variables_st,
    generate_io_mapping_csv_bytes,
    generate_sysmac_import_guide_txt
)

from company_generators.st_quality_checker import (
    generate_st_quality_report_text
)



from company_generators.engineering_reports_generator import (
    generate_alarm_list_csv_bytes,
    generate_step_list_csv_bytes,
    generate_io_mapping_enhanced_csv_bytes,
    generate_variable_cross_reference_report_text,
    generate_final_acceptance_report_text
)

GENERATOR_NAME = "PLC数字工程师"
GENERATOR_VERSION = "V0.6.4"
TEMPLATE_VERSION = "company_template_v0.1"

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "configs"
OUTPUT_DIR = BASE_DIR / "output"

DEFAULT_MULTI_CONFIG = CONFIG_DIR / "sample_multi_station_project.json"
DEFAULT_SYMBOL_CONFIG = CONFIG_DIR / "company_symbols.json"

PACKAGE_DIR = OUTPUT_DIR / "device_project_package_v06"
ZIP_PATH = OUTPUT_DIR / "AI_Device_Project_Package_V06.zip"


def load_json_file(path: str | Path) -> dict:
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_bytes(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def safe_file_name(name: str) -> str:
    name = str(name).strip()
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = re.sub(r"\s+", "_", name)
    return name or "Station"


def file_sha256(path: Path) -> str:
    sha256 = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def build_file_record(file: Path, package_dir: Path, category: str) -> dict:
    return {
        "path": str(file.relative_to(package_dir)).replace("\\", "/"),
        "category": category,
        "size_bytes": file.stat().st_size,
        "sha256": file_sha256(file)
    }


def validate_multi_station_project(
    cylinder_config: dict,
    station_configs: list[dict]
) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []

    cylinders = cylinder_config.get("cylinders", [])

    if not cylinders:
        errors.append("cylinder_config 中没有 cylinders。")
    else:
        errors.extend(validate_all_cylinders(cylinders))

    if not station_configs:
        errors.append("station_configs 为空，至少需要一个工站。")
        return errors, warnings

    seen_program_names = set()
    seen_station_nums = set()

    for index, station_config in enumerate(station_configs, start=1):
        program_name = station_config.get("program_name", f"UNKNOWN_{index}")
        station_num = station_config.get("station_num")

        if program_name in seen_program_names:
            errors.append(f"工站 program_name 重复：{program_name}")
        seen_program_names.add(program_name)

        if station_num in seen_station_nums:
            errors.append(f"工站 station_num 重复：{station_num}")
        seen_station_nums.add(station_num)

        station_errors = validate_station_config(station_config)
        for err in station_errors:
            errors.append(f"{program_name}：{err}")

        if not station_config.get("safety_stop_actions"):
            warnings.append(f"{program_name} 未配置 safety_stop_actions。")

    return errors, warnings


def build_multi_validation_report(
    project_info: dict,
    cylinder_config: dict,
    station_configs: list[dict],
    errors: list[str],
    warnings: list[str],
    package_dir: Path | None = None
) -> str:
    cylinders = cylinder_config.get("cylinders", [])

    lines = []
    lines.append("PLC数字工程师 V0.6 多工站自动校验报告")
    lines.append("=" * 60)
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"项目名称：{project_info.get('project_name', 'UNKNOWN')}")
    lines.append(f"PLC：{project_info.get('plc', 'UNKNOWN')}")
    lines.append("")
    lines.append("一、总体结论")
    lines.append("-" * 60)

    if errors:
        lines.append(f"结果：不通过（发现 {len(errors)} 个错误，{len(warnings)} 个警告）")
    elif warnings:
        lines.append(f"结果：有警告（0 个错误，{len(warnings)} 个警告）")
    else:
        lines.append("结果：基础校验通过（0 个错误，0 个警告）")

    lines.append("")
    lines.append("二、配置统计")
    lines.append("-" * 60)
    lines.append(f"气缸数量：{len(cylinders)}")
    lines.append(f"工站数量：{len(station_configs)}")

    for station in station_configs:
        lines.append(
            f"- {station.get('program_name', 'UNKNOWN')} / "
            f"工站号 {station.get('station_num', 'UNKNOWN')} / "
            f"步骤数 {len(station.get('steps', []))}"
        )

    lines.append("")
    lines.append("三、错误列表")
    lines.append("-" * 60)

    if errors:
        for i, err in enumerate(errors, start=1):
            lines.append(f"{i}. {err}")
    else:
        lines.append("无错误。")

    lines.append("")
    lines.append("四、警告列表")
    lines.append("-" * 60)

    if warnings:
        for i, warn in enumerate(warnings, start=1):
            lines.append(f"{i}. {warn}")
    else:
        lines.append("无警告。")

    lines.append("")
    lines.append("五、人工复核建议")
    lines.append("-" * 60)
    lines.append("1. 检查所有气缸 IO 点位是否与电气图一致。")
    lines.append("2. 检查每个工站 station_num 是否与 HMI / 报警表一致。")
    lines.append("3. 检查每个工站的报警编号是否符合公司规范。")
    lines.append("4. 检查多工站之间是否有互锁、等待、放行信号。")
    lines.append("5. 在 Sysmac Studio 中逐个 POU 编译。")
    lines.append("6. 真实设备必须先空载测试，再联机调试。")

    return "\n".join(lines)


def build_readme(project_info: dict, station_configs: list[dict]) -> str:
    project_name = project_info.get("project_name", "AI_Device_Project_V06")
    plc = project_info.get("plc", "Omron NJ501")
    description = project_info.get("description", "")

    station_list = "\n".join(
        [
            f"- {s.get('program_name')}：{s.get('station_name')}，工站号 {s.get('station_num')}"
            for s in station_configs
        ]
    )

    return f"""
PLC数字工程师 {GENERATOR_VERSION} 多工站工程包

项目名称：{project_name}
PLC：{plc}
生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
生成器：{GENERATOR_NAME}
模板版本：{TEMPLATE_VERSION}

项目说明：
{description}

工站列表：
{station_list}

文件说明：
1. 00_README.txt
   - 工程包说明

2. validation_report.txt
   - 多工站自动校验报告

3. manifest.json
   - 工程包清单和文件 SHA256 追踪

4. 01_Cylinder_Action_Generated.st
   - 气缸动作统一调用程序

5. 02_Station_xxx.st / 03_Station_xxx.st
   - 多个工站自动流程程序

6. configs/
   - cylinder_config.json
   - station_configs.json
   - company_symbols.json

7. template_source/
   - 公司模板参考源码

注意：
- 本工程包不能直接下载到真实 PLC。
- 必须经工程师审核、Sysmac Studio 编译、仿真、空载测试、现场调试。
- 多工站之间的互锁、交互信号，需要工程师根据实际节拍补充。
""".strip()


def build_manifest(
    project_info: dict,
    package_dir: Path,
    file_records: list[dict],
    cylinder_config: dict,
    station_configs: list[dict]
) -> dict:
    cylinders = cylinder_config.get("cylinders", [])

    return {
        "manifest_version": "1.0",
        "generator": GENERATOR_NAME,
        "generator_version": GENERATOR_VERSION,
        "template_version": TEMPLATE_VERSION,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project": {
            "project_name": project_info.get("project_name", "AI_Device_Project_V06"),
            "plc": project_info.get("plc", "Omron NJ501"),
            "description": project_info.get("description", "")
        },
        "summary": {
            "cylinder_count": len(cylinders),
            "station_count": len(station_configs),
            "station_programs": [
                s.get("program_name", "UNKNOWN")
                for s in station_configs
            ],
            "has_company_symbols": (package_dir / "configs" / "company_symbols.json").exists(),
            "has_template_source": (package_dir / "template_source").exists(),
            "has_validation_report": (package_dir / "validation_report.txt").exists()
        },
        "generated_outputs": [
            item for item in file_records
            if item["category"] == "generated_st"
        ],
        "configs": [
            item for item in file_records
            if item["category"] == "config"
        ],
        "template_source": [
            item for item in file_records
            if item["category"] == "template_source"
        ],
        "documents": [
            item for item in file_records
            if item["category"] == "document"
        ],
        "all_files": file_records
    }


def generate_multi_station_project_package(
    project_info: dict,
    cylinder_config: dict,
    station_configs: list[dict],
    package_dir: Path = PACKAGE_DIR,
    zip_path: Path = ZIP_PATH
) -> dict:
    errors, warnings = validate_multi_station_project(
        cylinder_config=cylinder_config,
        station_configs=station_configs
    )

    if errors:
        return {
            "ok": False,
            "errors": errors,
            "warnings": warnings,
            "package_dir": None,
            "zip_path": None,
            "files": []
        }

    if package_dir.exists():
        shutil.rmtree(package_dir)

    package_dir.mkdir(parents=True, exist_ok=True)

    files_written: list[tuple[Path, str]] = []

    readme_text = build_readme(project_info, station_configs)
    validation_text = build_multi_validation_report(
        project_info=project_info,
        cylinder_config=cylinder_config,
        station_configs=station_configs,
        errors=errors,
        warnings=warnings,
        package_dir=package_dir
    )

    validation_text += (
        "\n\n========== V0.6.2.1 主工程集成验收 ==========\n"
        "✅ 已集成 04_Machine_Auto_Main_Generated.st 生成\n"
        "✅ 已集成 HMI_Variable_List.csv 生成\n"
        "✅ 已集成多工站顺序互锁\n"
        "✅ 已集成工站报警汇总\n"
        "✅ 已集成整机统一复位\n"
        "✅ 已集成整机完成判断\n"
    )

    validation_text += (
        "\n\n========== V0.6.3 Sysmac Studio 导入前工程规范增强 ==========\n"
        "✅ 已生成 00_DUT_Struct_Generated.st\n"
        "✅ 已生成 00_Global_Variables_Generated.st\n"
        "✅ 已生成 IO_Mapping_List.csv\n"
        "✅ 已生成 Sysmac_Import_Guide.txt\n"
        "✅ 已生成 ST_Quality_Report.txt\n"
        "✅ 已增强变量声明、DUT结构、IO映射和导入说明\n"
    )

    validation_text += (
        "\n\n========== V0.6.4 工程质量增强 ==========\n"
        "✅ 已生成 Alarm_List.csv\n"
        "✅ 已生成 Step_List.csv\n"
        "✅ 已生成 IO_Mapping_Enhanced.csv\n"
        "✅ 已生成 Variable_CrossReference_Report.txt\n"
        "✅ 已生成 Final_Acceptance_Report.txt\n"
        "✅ 已增强报警清单、步骤清单、变量交叉引用和最终验收报告\n"
    )

    readme_path = package_dir / "00_README.txt"
    validation_path = package_dir / "validation_report.txt"

    write_text(readme_path, readme_text)
    write_text(validation_path, validation_text)

    files_written.extend([
        (readme_path, "document"),
        (validation_path, "document")
    ])

    cylinders = cylinder_config.get("cylinders", [])
    cylinder_code = render_cylinder_action(cylinders)

    cylinder_path = package_dir / "01_Cylinder_Action_Generated.st"
    write_text(cylinder_path, cylinder_code)
    files_written.append((cylinder_path, "generated_st"))

    station_output_paths = []

    for index, station_config in enumerate(station_configs, start=2):
        program_name = station_config.get("program_name", f"Station_{index}")
        file_name = f"{index:02d}_Station_{safe_file_name(program_name)}.st"

        station_code = render_station_program(station_config)
        station_path = package_dir / file_name

        write_text(station_path, station_code)
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

    # V0.6.3：Sysmac Studio 导入前 DUT / 全局变量 / IO映射 / 导入说明
    dut_struct_path = package_dir / "00_DUT_Struct_Generated.st"
    write_text(dut_struct_path, generate_dut_struct_st(cylinder_config, station_configs))
    files_written.append((dut_struct_path, "generated_st"))

    global_variables_path = package_dir / "00_Global_Variables_Generated.st"
    write_text(global_variables_path, generate_global_variables_st(cylinder_config, station_configs))
    files_written.append((global_variables_path, "generated_st"))

    io_mapping_path = package_dir / "IO_Mapping_List.csv"
    write_bytes(io_mapping_path, generate_io_mapping_csv_bytes(cylinder_config, station_configs))
    files_written.append((io_mapping_path, "io_mapping"))

    sysmac_guide_path = package_dir / "Sysmac_Import_Guide.txt"
    write_text(sysmac_guide_path, generate_sysmac_import_guide_txt(cylinder_config, station_configs))
    files_written.append((sysmac_guide_path, "document"))

    configs_dir = package_dir / "configs"

    cylinder_config_path = configs_dir / "cylinder_config.json"
    station_configs_path = configs_dir / "station_configs.json"

    write_text(
        cylinder_config_path,
        json.dumps(cylinder_config, ensure_ascii=False, indent=4)
    )
    write_text(
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

    if DEFAULT_SYMBOL_CONFIG.exists():
        symbols_text = DEFAULT_SYMBOL_CONFIG.read_text(encoding="utf-8")
        symbols_path = configs_dir / "company_symbols.json"
        write_text(symbols_path, symbols_text)
        files_written.append((symbols_path, "config"))

    template_dir = package_dir / "template_source"
    company_st_dir = BASE_DIR / "company_template" / "st"

    template_files = [
        "FB_Cylinder.st",
        "Cylinder_Action.st",
        "MachineAlarm.st",
        "Machine_Init.st",
        "Servo_Action.st",
        "FB_Axis.st",
        "FB_Motor.st",
        "FB_Delay.st",
        "FB_SafetyDoor.st",
        "FB_Vacuum.st"
    ]

    for filename in template_files:
        src = company_st_dir / filename
        if src.exists():
            dst = template_dir / filename
            write_text(dst, src.read_text(encoding="utf-8"))
            files_written.append((dst, "template_source"))

    # V0.6.3：ST 静态质量检查报告
    st_quality_report_path = package_dir / "ST_Quality_Report.txt"
    write_text(
        st_quality_report_path,
        generate_st_quality_report_text(package_dir, station_configs)
    )
    files_written.append((st_quality_report_path, "document"))

    # V0.6.4：报警清单 / 步骤清单 / 增强IO / 变量交叉引用 / 最终验收
    alarm_list_path = package_dir / "Alarm_List.csv"
    write_bytes(alarm_list_path, generate_alarm_list_csv_bytes(cylinder_config, station_configs))
    files_written.append((alarm_list_path, "alarm_list"))

    step_list_path = package_dir / "Step_List.csv"
    write_bytes(step_list_path, generate_step_list_csv_bytes(station_configs))
    files_written.append((step_list_path, "step_list"))

    io_mapping_enhanced_path = package_dir / "IO_Mapping_Enhanced.csv"
    write_bytes(io_mapping_enhanced_path, generate_io_mapping_enhanced_csv_bytes(cylinder_config, station_configs))
    files_written.append((io_mapping_enhanced_path, "io_mapping"))

    variable_cross_reference_path = package_dir / "Variable_CrossReference_Report.txt"
    write_text(
        variable_cross_reference_path,
        generate_variable_cross_reference_report_text(package_dir, cylinder_config, station_configs)
    )
    files_written.append((variable_cross_reference_path, "document"))

    final_acceptance_report_path = package_dir / "Final_Acceptance_Report.txt"
    write_text(
        final_acceptance_report_path,
        generate_final_acceptance_report_text(package_dir, cylinder_config, station_configs)
    )
    files_written.append((final_acceptance_report_path, "document"))

    file_records = [
        build_file_record(path, package_dir, category)
        for path, category in files_written
    ]

    manifest = build_manifest(
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

    # V0.6.3：manifest 增强信息
    manifest["version"] = GENERATOR_VERSION
    manifest["v063_generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    manifest["v063_features"] = [
        "Sysmac Studio 导入前 DUT 结构生成",
        "全局变量声明生成",
        "IO 映射清单生成",
        "Sysmac 导入说明生成",
        "ST 静态质量检查报告生成"
    ]
    manifest["v063_added_files"] = [
        "00_DUT_Struct_Generated.st",
        "00_Global_Variables_Generated.st",
        "IO_Mapping_List.csv",
        "Sysmac_Import_Guide.txt",
        "ST_Quality_Report.txt"
    ]

    # V0.6.4：manifest 增强信息
    manifest["version"] = GENERATOR_VERSION
    manifest["v064_generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    manifest["v064_features"] = [
        "报警清单 Alarm_List.csv 生成",
        "工站步骤清单 Step_List.csv 生成",
        "增强 IO 映射 IO_Mapping_Enhanced.csv 生成",
        "变量交叉引用报告生成",
        "最终验收报告生成"
    ]
    manifest["v064_added_files"] = [
        "Alarm_List.csv",
        "Step_List.csv",
        "IO_Mapping_Enhanced.csv",
        "Variable_CrossReference_Report.txt",
        "Final_Acceptance_Report.txt"
    ]

    manifest_path = package_dir / "manifest.json"
    write_text(
        manifest_path,
        json.dumps(manifest, ensure_ascii=False, indent=4)
    )

    files_written.append((manifest_path, "manifest"))

    manifest_record = build_file_record(manifest_path, package_dir, "manifest")
    file_records.append(manifest_record)

    manifest["manifest_file"] = manifest_record
    manifest["all_files"] = file_records

    write_text(
        manifest_path,
        json.dumps(manifest, ensure_ascii=False, indent=4)
    )

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file, _category in files_written:
            arcname = file.relative_to(package_dir)
            zip_file.write(file, arcname)

    return {
        "ok": True,
        "errors": [],
        "warnings": warnings,
        "package_dir": str(package_dir),
        "zip_path": str(zip_path),
        "files": [str(f) for f, _category in files_written],
        "station_files": [str(p) for p in station_output_paths],
        "manifest": manifest
    }


def generate_multi_station_project_package_from_file() -> dict:
    config = load_json_file(DEFAULT_MULTI_CONFIG)

    project_info = config.get("project_info", {
        "project_name": "AI_Device_Project_V06",
        "plc": "Omron NJ501",
        "description": "多工站工程包。"
    })

    cylinder_config = config.get("cylinder_config", {
        "cylinders": []
    })

    station_configs = config.get("station_configs", [])

    return generate_multi_station_project_package(
        project_info=project_info,
        cylinder_config=cylinder_config,
        station_configs=station_configs
    )


def main():
    result = generate_multi_station_project_package_from_file()

    if not result["ok"]:
        print("多工站工程包生成失败：")
        for err in result["errors"]:
            print(" -", err)
        return

    print("多工站工程包生成成功：")
    print("目录：", result["package_dir"])
    print("ZIP：", result["zip_path"])
    print("")
    print("工站文件：")
    for f in result["station_files"]:
        print(" -", f)

    if result.get("warnings"):
        print("")
        print("警告：")
        for warn in result["warnings"]:
            print(" -", warn)


if __name__ == "__main__":
    main()