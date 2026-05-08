from pathlib import Path
import zipfile

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")

def find_latest_zip():
    zips = []
    for p in PROJECT_DIR.rglob("*.zip"):
        p_str = str(p).lower()
        p_name = p.name.lower()

        if ".venv" in p_str:
            continue

        # 跳过源码备份包
        if "source_backup" in p_name:
            continue

        # 跳过普通备份包
        if "backup" in p_name:
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

def check_keywords(text, keywords):
    return [kw for kw in keywords if kw.lower() in text.lower()]

def main():
    zip_path = find_latest_zip()
    if not zip_path:
        print("❌ 没找到 ZIP 文件")
        return

    print("正在最终验收 ZIP：")
    print(zip_path)

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

        st_files = [
            n for n in names
            if n.lower().endswith(".st")
        ]

        print("\n========== ST 文件 ==========")
        for f in st_files:
            print(f)

        s1_file = next((n for n in st_files if "S1" in n), None)
        s2_file = next((n for n in st_files if "S2" in n), None)

        if not s1_file:
            print("❌ 未找到 S1 ST 文件")
            return

        if not s2_file:
            print("❌ 未找到 S2 ST 文件")
            return

        s1_text = read_text(z, s1_file)
        s2_text = read_text(z, s2_file)
        all_text = s1_text + "\n" + s2_text

        print("\n========== 1. S2 等待 S1 完成检查 ==========")

        wait_s1_keywords = [
            "S1",
            "Station_1",
            "Station[S1]",
            "Prev",
            "Previous",
            "前工站",
            "上一工站",
            "Done",
            "Complete",
            "完成"
        ]

        hit_wait = check_keywords(s2_text, wait_s1_keywords)

        if "S1" in s2_text and ("Done" in s2_text or "Complete" in s2_text or "完成" in s2_text):
            print("✅ S2 ST 中明确出现 S1 完成相关逻辑")
        elif hit_wait:
            print("⚠️ S2 ST 中出现部分前工站关键词：", hit_wait)
            print("需要人工看一下是否真的是等待 S1 完成")
        else:
            print("❌ S2 ST 中没有明显等待 S1 完成逻辑")

        print("\n========== 2. Reset 复位逻辑检查 ==========")

        reset_keywords = [
            "bReset",
            "Reset",
            "复位",
            "AutoStep := 0",
            "nAutoStep := 0",
            "Alarm := FALSE",
            "bAlarm := FALSE"
        ]

        hit_reset = check_keywords(all_text, reset_keywords)

        if hit_reset:
            print("✅ ST 中发现复位相关关键词：", hit_reset)
        else:
            print("⚠️ ST 中没有明显复位逻辑")
            print("说明：符号表里有 reset，但生成的 ST 里可能还没真正处理 reset")

        print("\n========== 3. 报警逻辑检查 ==========")

        alarm_keywords = [
            "Alarm",
            "bAlarm",
            "Timeout",
            "TON",
            "超时",
            "报警"
        ]

        hit_alarm = check_keywords(all_text, alarm_keywords)

        if hit_alarm:
            print("✅ ST 中发现报警/超时相关关键词：", hit_alarm)
        else:
            print("❌ ST 中没有明显报警/超时逻辑")

        print("\n========== 最终结论 ==========")

        if hit_alarm and hit_reset and hit_wait:
            print("✅ V0.6.1 最终验收通过，可以封版")
        else:
            print("⚠️ V0.6.1 基础通过，但建议补强上面提示项后再封版")

if __name__ == "__main__":
    main()