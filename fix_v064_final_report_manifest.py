from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path(r"D:\AI\plc_ai_system\company_generators\engineering_reports_generator.py")

def main():
    if not TARGET.exists():
        print("❌ 找不到：", TARGET)
        return

    backup = TARGET.with_name(
        f"{TARGET.stem}_backup_fix_manifest_v064_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    )
    shutil.copy2(TARGET, backup)
    print("✅ 已备份：", backup)

    text = TARGET.read_text(encoding="utf-8", errors="ignore")

    remove_items = [
        '        "manifest.json",\n',
        '        "Final_Acceptance_Report.txt",\n',
    ]

    changed = 0

    for item in remove_items:
        if item in text:
            text = text.replace(item, "")
            changed += 1
            print("✅ 已移除自检项：", item.strip())
        else:
            print("⚠️ 未找到自检项，可能已经移除：", item.strip())

    TARGET.write_text(text, encoding="utf-8")

    print(f"\n✅ 修复完成，共处理 {changed} 项")
    print("说明：manifest.json 和 Final_Acceptance_Report.txt 不再参与最终报告生成时的提前自检。")

if __name__ == "__main__":
    main()