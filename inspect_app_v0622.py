from pathlib import Path
import re

APP = Path(r"D:\AI\plc_ai_system\app.py")

def main():
    if not APP.exists():
        print("❌ app.py 不存在")
        return

    text = APP.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    print("========== app.py 基本信息 ==========")
    print(APP)
    print("总行数：", len(lines))

    print("\n========== 1. 版本字符串扫描 ==========")
    version_patterns = [
        "V0.6",
        "V0.6.1",
        "V0.6.2",
        "V0.6.2.1",
        "V0.6.2.2",
    ]

    for v in version_patterns:
        count = text.count(v)
        print(f"{v}: {count} 次")

    print("\n========== 2. 多工站生成器调用扫描 ==========")
    keywords = [
        "generate_multi_station_project_package",
        "generate_multi_station_project_package_from_file",
        "multi_station_project_generator",
        "AI_Device_Project_Package_V06.zip",
        "download_button",
        "st.download_button",
        "zip_path",
        "station_configs",
        "multi_station",
        "整机",
        "多工站",
    ]

    for kw in keywords:
        print(f"\n--- {kw} ---")
        found = False
        for i, line in enumerate(lines, start=1):
            if kw in line:
                print(f"{i:04d}: {line}")
                found = True
        if not found:
            print("未找到")

    print("\n========== 3. 可能需要改版本显示的位置 ==========")
    for i, line in enumerate(lines, start=1):
        if "V0." in line or "版本" in line or "version" in line.lower():
            print(f"{i:04d}: {line}")

if __name__ == "__main__":
    main()