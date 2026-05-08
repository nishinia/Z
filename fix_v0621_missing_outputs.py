from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path(r"D:\AI\plc_ai_system\company_generators\multi_station_project_generator.py")


def main():
    text = TARGET.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")

    backup = TARGET.parent / f"{TARGET.stem}_fix_missing_outputs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy2(TARGET, backup)
    print("✅ 已备份：", backup)

    if "machine_main_path = package_dir / \"04_Machine_Auto_Main_Generated.st\"" in text:
        print("✅ 04 和 HMI 生成代码已经存在，不需要重复修复")
        return

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

    if old not in text:
        print("❌ 没找到插入点，先不要手改")
        print("请运行：python inspect_generate_package_func.py")
        return

    text = text.replace(old, new, 1)

    TARGET.write_text(text, encoding="utf-8")
    print("✅ 已补入 04_Machine_Auto_Main_Generated.st 和 HMI_Variable_List.csv 生成逻辑")


if __name__ == "__main__":
    main()