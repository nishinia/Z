from pathlib import Path
import zipfile
import csv
import io

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")


def find_latest_v062_zip():
    zips = []

    for p in PROJECT_DIR.rglob("*.zip"):
        p_str = str(p).lower()
        p_name = p.name.lower()

        if ".venv" in p_str:
            continue

        if "source_backup" in p_name:
            continue

        if "backup" in p_name:
            continue

        if "v0.6.2" not in p_name:
            continue

        zips.append(p)

    if not zips:
        return None

    return max(zips, key=lambda x: x.stat().st_mtime)


def read_text(z, name):
    raw = z.read(name)
    for enc in ["utf-8-sig", "utf-8", "gbk"]:
        try:
            return raw.decode(enc)
        except Exception:
            pass
    return raw.decode("utf-8", errors="ignore")


def find_endswith(names, suffix):
    for n in names:
        if n.replace("\\", "/").endswith(suffix):
            return n
    return None


def main():
    zip_path = find_latest_v062_zip()

    if not zip_path:
        print("❌ 没找到 V0.6.2 ZIP")
        return

    print("正在检查 V0.6.2 ZIP：")
    print(zip_path)

    ok = True

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

        required = [
            "00_README.txt",
            "validation_report.txt",
            "manifest.json",
            "01_Cylinder_Action_Generated.st",
            "02_Station_S1_Auto_Generated.st",
            "03_Station_S2_Auto_Generated.st",
            "04_Machine_Auto_Main_Generated.st",
            "HMI_Variable_List.csv",
            "configs/v062_station_chain.json",
        ]

        print("\n========== 1. 必要文件检查 ==========")

        for f in required:
            hit = find_endswith(names, f)
            if hit:
                print(f"✅ {f}")
            else:
                print(f"❌ 缺少 {f}")
                ok = False

        print("\n========== 2. 整机主流程 ST 检查 ==========")

        machine_st_name = find_endswith(names, "04_Machine_Auto_Main_Generated.st")

        if not machine_st_name:
            print("❌ 未找到 04_Machine_Auto_Main_Generated.st")
            ok = False
        else:
            text = read_text(z, machine_st_name)

            checks = {
                "整机就绪 bReady": "bReady",
                "运行许可 bCanRun": "bCanRun",
                "报警汇总 bAnyStationAlarm": "bAnyStationAlarm",
                "统一复位 bReset": "bReset",
                "S1 使能 Station[1].bEnable": "Station[1].bEnable",
                "S2 使能 Station[2].bEnable": "Station[2].bEnable",
                "S2 等待 S1 Done": "Station[1].bDone",
                "整机完成 bComplete": "bComplete",
            }

            for label, kw in checks.items():
                if kw in text:
                    print(f"✅ {label}")
                else:
                    print(f"❌ 缺少：{label}")
                    ok = False

        print("\n========== 3. HMI 变量清单检查 ==========")

        hmi_name = find_endswith(names, "HMI_Variable_List.csv")

        if not hmi_name:
            print("❌ 未找到 HMI_Variable_List.csv")
            ok = False
        else:
            raw = z.read(hmi_name)
            text = raw.decode("utf-8-sig", errors="ignore")
            reader = csv.reader(io.StringIO(text))
            rows = list(reader)

            print(f"✅ HMI CSV 行数：{len(rows)}")

            hmi_text = "\n".join([",".join(r) for r in rows])

            hmi_checks = [
                "Machine_Auto.bReady",
                "Machine_Auto.bCanRun",
                "Machine_Auto.bAnyStationAlarm",
                "Machine_Auto.bComplete",
                "Station[1].nAutoStep",
                "Station[1].bEnable",
                "Station[2].nAutoStep",
                "Station[2].bEnable",
                "Machine_Alarm.StationAlarm[1].Alarm",
                "Machine_Alarm.StationAlarm[2].Alarm",
            ]

            for kw in hmi_checks:
                if kw in hmi_text:
                    print(f"✅ HMI 包含：{kw}")
                else:
                    print(f"⚠️ HMI 未包含：{kw}")

        print("\n========== 4. validation_report 检查 ==========")

        val_name = find_endswith(names, "validation_report.txt")

        if val_name:
            val_text = read_text(z, val_name)
            if "V0.6.2" in val_text:
                print("✅ validation_report.txt 已写入 V0.6.2 验收信息")
            else:
                print("⚠️ validation_report.txt 未看到 V0.6.2 字样")
        else:
            print("❌ 未找到 validation_report.txt")
            ok = False

        print("\n========== V0.6.2 检查结论 ==========")

        if ok:
            print("✅ V0.6.2 ZIP 检查通过")
        else:
            print("❌ V0.6.2 ZIP 仍有缺失，需要修复")


if __name__ == "__main__":
    main()