from pathlib import Path
import zipfile
import json

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")

REQUIRED_FILES = [
    "00_README.txt",
    "validation_report.txt",
    "manifest.json",
    "01_Cylinder_Action_Generated.st",
    "02_Station_S1_Auto_Generated.st",
    "03_Station_S2_Auto_Generated.st",
]

REQUIRED_FOLDERS = [
    "configs",
    "template_source",
]

def find_latest_zip():
    zips = []
    for p in PROJECT_DIR.rglob("*.zip"):
        if ".venv" in str(p):
            continue
        zips.append(p)

    if not zips:
        return None

    return max(zips, key=lambda p: p.stat().st_mtime)

def has_file(names, filename):
    return any(n.replace("\\", "/").endswith(filename) for n in names)

def has_folder(names, folder):
    folder = folder.strip("/") + "/"
    return any(folder in n.replace("\\", "/") for n in names)

def main():
    zip_path = find_latest_zip()

    if zip_path is None:
        print("❌ 没找到 ZIP 文件")
        print("说明：你可能还没有在 Streamlit 界面生成 V0.6.1 工程包。")
        return

    print("正在检查最新 ZIP：")
    print(zip_path)

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

        print("\n========== ZIP 文件清单 ==========")
        for n in names:
            print(n)

        ok = True

        print("\n========== 必要文件检查 ==========")
        for f in REQUIRED_FILES:
            if has_file(names, f):
                print(f"✅ {f}")
            else:
                print(f"❌ 缺少 {f}")
                ok = False

        print("\n========== 必要目录检查 ==========")
        for folder in REQUIRED_FOLDERS:
            if has_folder(names, folder):
                print(f"✅ {folder}/")
            else:
                print(f"❌ 缺少 {folder}/")
                ok = False

        print("\n========== manifest.json 检查 ==========")
        manifest = next(
            (n for n in names if n.replace("\\", "/").endswith("manifest.json")),
            None
        )

        if manifest:
            try:
                data = json.loads(z.read(manifest).decode("utf-8"))
                print(json.dumps(data, ensure_ascii=False, indent=2))
            except Exception as e:
                print("❌ manifest.json 读取失败：", e)
                ok = False
        else:
            print("❌ 未找到 manifest.json")
            ok = False

        print("\n========== configs JSON 检查 ==========")
        config_jsons = [
            n for n in names
            if "/configs/" in "/" + n.replace("\\", "/") and n.endswith(".json")
        ]

        if not config_jsons:
            print("⚠️ configs 目录下没有 JSON 文件")
        else:
            for cfg in config_jsons:
                print(f"\n--- {cfg} ---")
                try:
                    data = json.loads(z.read(cfg).decode("utf-8"))
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                except Exception as e:
                    print("❌ JSON 读取失败：", e)
                    ok = False

        print("\n========== V0.6.1 检查结论 ==========")
        if ok:
            print("✅ ZIP 基础结构检查通过")
        else:
            print("❌ ZIP 结构不完整，需要修复生成器")

if __name__ == "__main__":
    main()