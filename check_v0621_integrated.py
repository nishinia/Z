from pathlib import Path
import zipfile
import csv
import io
import json

ZIP_PATH = Path(r"D:\AI\plc_ai_system\output\AI_Device_Project_Package_V06.zip")


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
    if not ZIP_PATH.exists():
        print("❌ ZIP 不存在：", ZIP_PATH)
        return

    print("正在检查 V0.6.2.1 主生成器集成包：")
    print(ZIP_PATH)

    ok = True

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
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
            "configs/cylinder_config.json",
            "configs/station_configs.json",
            "configs/v062_station_chain.json",
        ]

        print("\n========== 1. 必要文件检查 ==========")
        for f in required:
            if find_endswith(names, f):
                print(f"✅ {f}")
            else:
                print(f"❌ 缺少 {f}")
                ok = False

        print("\n========== 2. 整机主流程 ST 检查 ==========")
        machine_name = find_endswith(names, "04_Machine_Auto_Main_Generated.st")
        if machine_name:
            text = read_text(z, machine_name)

            checks = {
                "整机就绪 bReady": "bReady",
                "运行许可 bCanRun": "bCanRun",
                "报警汇总 bAnyStationAlarm": "bAnyStationAlarm",
                "统一复位 bReset": "bReset",
                "S1 使能": "Station[1].bEnable",
                "S2 使能": "Station[2].bEnable",
                "S2 等待 S1 Done": "Station[1].bDone",
                "整机完成": "bComplete",
            }

            for label, kw in checks.items():
                if kw in text:
                    print(f"✅ {label}")
                else:
                    print(f"❌ 缺少 {label}")
                    ok = False
        else:
            print("❌ 未找到 04_Machine_Auto_Main_Generated.st")
            ok = False

        print("\n========== 3. HMI CSV 检查 ==========")
        hmi_name = find_endswith(names, "HMI_Variable_List.csv")
        if hmi_name:
            hmi_text = read_text(z, hmi_name)
            rows = list(csv.reader(io.StringIO(hmi_text)))
            print(f"✅ HMI CSV 行数：{len(rows)}")

            hmi_checks = [
                "Machine_Auto.bReady",
                "Machine_Auto.bCanRun",
                "Machine_Auto.bAnyStationAlarm",
                "Machine_Auto.bComplete",
                "Station[1].nAutoStep",
                "Station[2].nAutoStep",
                "Machine_Alarm.StationAlarm[1].Alarm",
                "Machine_Alarm.StationAlarm[2].Alarm",
            ]

            for kw in hmi_checks:
                if kw in hmi_text:
                    print(f"✅ HMI 包含：{kw}")
                else:
                    print(f"❌ HMI 缺少：{kw}")
                    ok = False
        else:
            print("❌ 未找到 HMI_Variable_List.csv")
            ok = False

        print("\n========== 4. manifest 检查 ==========")
        manifest_name = find_endswith(names, "manifest.json")
        if manifest_name:
            manifest_text = read_text(z, manifest_name)
            manifest = json.loads(manifest_text)

            print("generator_version =", manifest.get("generator_version"))
            print("version =", manifest.get("version"))

            if "V0.6.2.1" in manifest_text:
                print("✅ manifest 已写入 V0.6.2.1")
            else:
                print("❌ manifest 未写入 V0.6.2.1")
                ok = False

            if "04_Machine_Auto_Main_Generated.st" in manifest_text:
                print("✅ manifest 包含整机主流程 ST")
            else:
                print("❌ manifest 缺少整机主流程 ST")
                ok = False

            if "HMI_Variable_List.csv" in manifest_text:
                print("✅ manifest 包含 HMI 变量清单")
            else:
                print("❌ manifest 缺少 HMI 变量清单")
                ok = False
        else:
            print("❌ 未找到 manifest.json")
            ok = False

        print("\n========== 5. validation_report 检查 ==========")
        val_name = find_endswith(names, "validation_report.txt")
        if val_name:
            val_text = read_text(z, val_name)
            if "V0.6.2.1" in val_text:
                print("✅ validation_report 已写入 V0.6.2.1")
            else:
                print("❌ validation_report 未写入 V0.6.2.1")
                ok = False
        else:
            print("❌ 未找到 validation_report.txt")
            ok = False

    print("\n========== V0.6.2.1 集成验收结论 ==========")
    if ok:
        print("✅ V0.6.2.1 主工程生成器集成通过")
    else:
        print("❌ V0.6.2.1 集成仍有问题")


if __name__ == "__main__":
    main()