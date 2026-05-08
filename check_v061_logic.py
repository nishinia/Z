from pathlib import Path
import zipfile
import json

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")

def find_latest_zip():
    zips = []
    for p in PROJECT_DIR.rglob("*.zip"):
        if ".venv" in str(p):
            continue
        zips.append(p)
    if not zips:
        return None
    return max(zips, key=lambda p: p.stat().st_mtime)

def read_text(z, name):
    raw = z.read(name)
    for enc in ["utf-8", "utf-8-sig", "gbk"]:
        try:
            return raw.decode(enc)
        except Exception:
            pass
    return raw.decode("utf-8", errors="ignore")

def main():
    zip_path = find_latest_zip()
    if not zip_path:
        print("❌ 没找到 ZIP")
        return

    print("正在检查最新 ZIP：")
    print(zip_path)

    ok = True

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()
        norm_names = [n.replace("\\", "/") for n in names]

        print("\n========== 1. 检查工站 ST 文件 ==========")

        s1_file = next((n for n in names if n.replace("\\", "/").endswith("02_Station_S1_Auto_Generated.st")), None)
        s2_file = next((n for n in names if n.replace("\\", "/").endswith("03_Station_S2_Auto_Generated.st")), None)

        if s1_file:
            print("✅ 找到 S1 ST 文件：", s1_file)
        else:
            print("❌ 缺少 S1 ST 文件")
            ok = False

        if s2_file:
            print("✅ 找到 S2 ST 文件：", s2_file)
        else:
            print("❌ 缺少 S2 ST 文件")
            ok = False

        print("\n========== 2. 检查 S1 / S2 ST 内容关键词 ==========")

        if s1_file:
            s1_text = read_text(z, s1_file)
            s1_keywords = ["S1", "Step", "Done", "Alarm"]
            for kw in s1_keywords:
                if kw in s1_text or kw.lower() in s1_text.lower():
                    print(f"✅ S1 包含关键词：{kw}")
                else:
                    print(f"⚠️ S1 未明显包含关键词：{kw}")

            if "夹紧" in s1_text or "顶升" in s1_text or "Clamp" in s1_text or "Lift" in s1_text:
                print("✅ S1 似乎包含上料夹紧/顶升相关逻辑")
            else:
                print("⚠️ S1 未明显看到夹紧/顶升关键词，可能是变量已英文标准化")

        if s2_file:
            s2_text = read_text(z, s2_file)
            s2_keywords = ["S2", "Step", "Done", "Alarm"]
            for kw in s2_keywords:
                if kw in s2_text or kw.lower() in s2_text.lower():
                    print(f"✅ S2 包含关键词：{kw}")
                else:
                    print(f"⚠️ S2 未明显包含关键词：{kw}")

            if "压装" in s2_text or "Press" in s2_text:
                print("✅ S2 似乎包含压装相关逻辑")
            else:
                print("⚠️ S2 未明显看到压装关键词，可能是变量已英文标准化")

            if "S1" in s2_text or "Prev" in s2_text or "前工站" in s2_text:
                print("✅ S2 似乎包含等待 S1 / 前工站完成逻辑")
            else:
                print("⚠️ S2 未明显看到等待 S1 完成逻辑")

        print("\n========== 3. 检查 configs JSON ==========")

        config_jsons = [
            n for n in names
            if "/configs/" in "/" + n.replace("\\", "/") and n.endswith(".json")
        ]

        if not config_jsons:
            print("❌ configs 下没有 JSON")
            ok = False
        else:
            for cfg in config_jsons:
                print(f"\n--- {cfg} ---")
                try:
                    data = json.loads(read_text(z, cfg))
                    print(json.dumps(data, ensure_ascii=False, indent=2))

                    text = json.dumps(data, ensure_ascii=False)

                    if "S1" in text:
                        print("✅ JSON 中包含 S1")
                    if "S2" in text:
                        print("✅ JSON 中包含 S2")
                    if "上料" in text or "夹紧" in text or "顶升" in text:
                        print("✅ JSON 中包含 S1 工艺特征")
                    if "压装" in text:
                        print("✅ JSON 中包含 S2 工艺特征")
                    if "超时" in text or "报警" in text or "timeout" in text.lower() or "alarm" in text.lower():
                        print("✅ JSON 中包含报警/超时特征")
                    if "复位" in text or "reset" in text.lower():
                        print("✅ JSON 中包含复位特征")

                except Exception as e:
                    print("❌ JSON 读取失败：", e)
                    ok = False

        print("\n========== V0.6.1 逻辑检查结论 ==========")
        if ok:
            print("✅ V0.6.1 文件结构正常，逻辑内容请根据上方关键词确认")
        else:
            print("❌ V0.6.1 存在明显缺失")

if __name__ == "__main__":
    main()