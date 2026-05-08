from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path(r"D:\AI\plc_ai_system\company_generators\engineering_reports_generator.py")

NEW_FUNC = '''
def generate_final_acceptance_report_text(package_dir, cylinder_config, station_configs):
    package_dir = Path(package_dir)
    stations = normalize_station_configs(station_configs)
    cylinders = normalize_cylinders(cylinder_config)

    required = [
        "00_README.txt",
        "validation_report.txt",
        "manifest.json",
        "00_DUT_Struct_Generated.st",
        "00_Global_Variables_Generated.st",
        "01_Cylinder_Action_Generated.st",
        "04_Machine_Auto_Main_Generated.st",
        "HMI_Variable_List.csv",
        "IO_Mapping_List.csv",
        "IO_Mapping_Enhanced.csv",
        "Alarm_List.csv",
        "Step_List.csv",
        "Variable_CrossReference_Report.txt",
        "Sysmac_Import_Guide.txt",
        "ST_Quality_Report.txt",
    ]

    lines = []
    lines.append("Final Acceptance Report - V0.6.4")
    lines.append("=" * 80)
    lines.append(f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Package Dir : {package_dir}")
    lines.append("")
    lines.append("一、工程概况")
    lines.append(f"工站数量：{len(stations)}")
    lines.append(f"气缸数量：{len(cylinders)}")

    if stations:
        lines.append("工站链路：" + " -> ".join([s["station_id"] for s in stations]))
    else:
        lines.append("工站链路：未识别到工站")

    lines.append("")
    lines.append("二、交付文件检查")

    missing = []

    for name in required:
        if (package_dir / name).exists():
            lines.append(f"✅ {name}")
        else:
            lines.append(f"❌ {name}")
            missing.append(name)

    lines.append("")
    lines.append("三、V0.6.4 新增交付物")
    lines.append("✅ Alarm_List.csv：报警清单")
    lines.append("✅ Step_List.csv：工站步骤清单")
    lines.append("✅ IO_Mapping_Enhanced.csv：增强 IO 映射")
    lines.append("✅ Variable_CrossReference_Report.txt：变量交叉引用报告")
    lines.append("✅ Final_Acceptance_Report.txt：最终验收报告")
    lines.append("")

    lines.append("四、结论")
    if missing:
        lines.append("FAIL: 存在缺失文件，请检查生成器。")
        lines.append("缺失文件：" + ", ".join(missing))
    else:
        lines.append("PASS: V0.6.4 工程包静态验收通过。")

    lines.append("")
    lines.append("注意：静态验收通过不代表可直接上机。")
    lines.append("正式投产前必须完成 Sysmac Studio 编译、仿真、IO 点检、单步调试和安全验证。")
    lines.append("")

    return chr(10).join(lines)
'''

def main():
    if not TARGET.exists():
        print("❌ 找不到：", TARGET)
        return

    backup = TARGET.with_name(
        f"{TARGET.stem}_backup_repair_v064_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    )
    shutil.copy2(TARGET, backup)
    print("✅ 已备份：", backup)

    text = TARGET.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")
    lines = text.splitlines()

    start_index = None

    for i, line in enumerate(lines):
        if line.startswith("def generate_final_acceptance_report_text("):
            start_index = i
            break

    if start_index is None:
        print("❌ 没找到 generate_final_acceptance_report_text 函数")
        return

    # 这个函数在文件末尾，直接从函数开始替换到文件结束
    new_lines = lines[:start_index]
    new_lines.append(NEW_FUNC.strip())

    TARGET.write_text(chr(10).join(new_lines) + chr(10), encoding="utf-8")

    print("✅ 已修复 engineering_reports_generator.py")
    print("✅ 已避免 return 换行字符串错误")

if __name__ == "__main__":
    main()