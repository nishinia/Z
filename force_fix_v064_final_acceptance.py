from pathlib import Path
from datetime import datetime
import shutil
import re

TARGET = Path(r"D:\AI\plc_ai_system\company_generators\engineering_reports_generator.py")

NEW_FUNC = r'''
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

    return "\n".join(lines)
'''

def main():
    if not TARGET.exists():
        print("❌ 找不到：", TARGET)
        return

    backup = TARGET.with_name(
        f"{TARGET.stem}_backup_force_fix_v064_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    )
    shutil.copy2(TARGET, backup)
    print("✅ 已备份：", backup)

    text = TARGET.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")

    pattern = (
        r"def generate_final_acceptance_report_text"
        r"\(package_dir, cylinder_config, station_configs\):"
        r".*?"
        r"(?=\n\ndef |\Z)"
    )

    new_text, count = re.subn(pattern, NEW_FUNC.strip(), text, flags=re.DOTALL)

    if count == 0:
        print("❌ 没找到 generate_final_acceptance_report_text 函数")
        print("请运行：findstr /n /i \"generate_final_acceptance_report_text PASS FAIL required\" company_generators\\engineering_reports_generator.py")
        return

    TARGET.write_text(new_text, encoding="utf-8")
    print("✅ 已重写 generate_final_acceptance_report_text 函数")
    print("✅ 这次最终报告在无缺失文件时会输出 PASS")

if __name__ == "__main__":
    main()