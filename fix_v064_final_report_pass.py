from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path(r"D:\AI\plc_ai_system\company_generators\engineering_reports_generator.py")

def main():
    if not TARGET.exists():
        print("❌ 找不到文件：", TARGET)
        return

    backup = TARGET.with_name(
        f"{TARGET.stem}_backup_fix_v064_pass_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    )
    shutil.copy2(TARGET, backup)
    print("✅ 已备份：", backup)

    text = TARGET.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")

    old = '''        "Variable_CrossReference_Report.txt",
        "Sysmac_Import_Guide.txt",
        "ST_Quality_Report.txt",
    ]
'''

    new = '''        "Variable_CrossReference_Report.txt",
        "Sysmac_Import_Guide.txt",
        "ST_Quality_Report.txt",
    ]

    # 注意：
    # Final_Acceptance_Report.txt 是当前函数正在生成的文件，
    # 不能在生成自身内容之前检查自己是否已经存在。
    # 否则会误判 FAIL。
'''

    if old not in text:
        print("⚠️ 没找到精确插入点，尝试直接移除自检项")

    # 删除 required 列表里的 Final_Acceptance_Report.txt
    text_new = text.replace('        "Final_Acceptance_Report.txt",\n', '')

    if text_new == text:
        print("⚠️ 没找到 Final_Acceptance_Report.txt 自检项，可能已经修过")
    else:
        print("✅ 已移除 Final_Acceptance_Report.txt 自检项")

    TARGET.write_text(text_new, encoding="utf-8")
    print("✅ V0.6.4 Final_Acceptance_Report PASS 修复完成")

if __name__ == "__main__":
    main()