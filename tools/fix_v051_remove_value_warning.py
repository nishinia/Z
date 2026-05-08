from pathlib import Path

APP_PATH = Path("app.py")
BACKUP_PATH = Path("app_backup_before_remove_value_warning.py")

text = APP_PATH.read_text(encoding="utf-8")
BACKUP_PATH.write_text(text, encoding="utf-8")

replacements = {
    '    value=default_project_info_v051,\n': '',
    '    value=default_cylinder_config_v051,\n': '',
    '    value=default_station_config_v051,\n': '',
}

count = 0

for old, new in replacements.items():
    n = text.count(old)
    count += n
    text = text.replace(old, new)

APP_PATH.write_text(text, encoding="utf-8")

print(f"已删除 value= 默认值行数量：{count}")
print("已备份原文件：app_backup_before_remove_value_warning.py")