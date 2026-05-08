from pathlib import Path
from datetime import datetime
import shutil

APP = Path(r"D:\AI\plc_ai_system\app.py")

def main():
    if not APP.exists():
        print("❌ app.py 不存在")
        return

    backup = APP.with_name(f"app_backup_v0622_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
    shutil.copy2(APP, backup)
    print("✅ 已备份：", backup)

    text = APP.read_text(encoding="utf-8", errors="ignore")

    replacements = {
        "🤖 V0.6.1 整机中文需求 → 多工站工程包":
            "🤖 V0.6.2.2 整机中文需求 → AI解析多工站 → V0.6.2.1工程包",

        "这一模块会把整机中文需求解析成多气缸、多工站配置，然后生成多工站工程包 ZIP。":
            "这一模块会把整机中文需求解析成多气缸、多工站配置，然后直接生成已集成整机主流程/HMI变量清单的 V0.6.2.1 工程包 ZIP。",

        "🤖 AI解析并生成 V0.6.1 多工站工程包":
            "🤖 AI解析并生成 V0.6.2.2 多工站整机工程包",

        "正在生成 V0.6.1 多工站工程包...":
            "正在生成 V0.6.2.2 多工站整机工程包...",

        "V0.6.1 多工站工程包生成失败：":
            "V0.6.2.2 多工站整机工程包生成失败：",

        "V0.6.1 多工站工程包生成完成。":
            "V0.6.2.2 多工站整机工程包生成完成。",

        "下载 V0.6.1 AI_Device_Project_Package_V061.zip":
            "下载 V0.6.2.2 AI_Device_Project_Package_V0622.zip",

        "AI_Device_Project_Package_V061.zip":
            "AI_Device_Project_Package_V0622.zip",

        "multi_station_config_ai_v061.json":
            "multi_station_config_ai_v0622.json",
    }

    changed = 0
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            print("✅ 替换：", old)
            changed += 1
        else:
            print("⚠️ 未找到：", old)

    APP.write_text(text, encoding="utf-8")

    print(f"\n✅ app.py 页面版本补丁完成，共替换 {changed} 项")
    print("说明：这是界面文字升级，不改变后端生成逻辑。")

if __name__ == "__main__":
    main()