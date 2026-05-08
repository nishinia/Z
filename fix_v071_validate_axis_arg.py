from pathlib import Path
from datetime import datetime
import shutil
import re

TARGET = Path(r"D:\AI\plc_ai_system\company_generators\multi_station_project_generator.py")


def main():
    if not TARGET.exists():
        print("❌ 找不到文件：", TARGET)
        return

    backup = TARGET.with_name(
        f"{TARGET.stem}_backup_fix_v071_validate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    )
    shutil.copy2(TARGET, backup)
    print("✅ 已备份：", backup)

    text = TARGET.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")

    old = '''    errors, warnings = validate_multi_station_project(
        cylinder_config=cylinder_config,
        station_configs=station_configs,
        axis_config=axis_config
    )
'''

    new = '''    errors, warnings = validate_multi_station_project(
        cylinder_config=cylinder_config,
        station_configs=station_configs
    )
'''

    if old in text:
        text = text.replace(old, new, 1)
        print("✅ 已修复 validate_multi_station_project 多余 axis_config 参数")
    else:
        print("⚠️ 没找到精确文本，尝试正则修复")

        pattern = (
            r"errors,\s*warnings\s*=\s*validate_multi_station_project\(\s*"
            r"cylinder_config=cylinder_config,\s*"
            r"station_configs=station_configs,\s*"
            r"axis_config=axis_config\s*"
            r"\)"
        )

        replacement = (
            "errors, warnings = validate_multi_station_project(\n"
            "        cylinder_config=cylinder_config,\n"
            "        station_configs=station_configs\n"
            "    )"
        )

        text, count = re.subn(pattern, replacement, text, count=1)

        if count:
            print("✅ 正则修复成功")
        else:
            print("❌ 没找到需要修复的位置")
            return

    TARGET.write_text(text, encoding="utf-8")
    print("✅ V0.7.1 validate 参数修复完成")


if __name__ == "__main__":
    main()