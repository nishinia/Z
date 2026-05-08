from pathlib import Path
import zipfile
import json
import csv
import io

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")
ZIP_PATH = PROJECT_DIR / "output" / "AI_Device_Project_Package_V06.zip"


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
    print("========== V0.6.3 自动生成工程包 ==========")

    from company_generators.multi_station_project_generator import generate_multi_station_project_package_from_file

    result = generate_multi_station_project_package_from_file()
    print("生成结果：", result.get("ok"))
    print("ZIP：", result.get("zip_path"))

    if not result.get("ok"):
        print("❌ 工程包生成失败：")
        for e in result.get("errors", []):
            print(e)
        return

    if not ZIP_PATH.exists():
        print("❌ ZIP 不存在：", ZIP_PATH)
        return

    print("\n========== V0.6.3 ZIP 检查 ==========")
    print(ZIP_PATH)

    ok = True

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        names = z.namelist()

        required = [
            "00_README.txt",
            "validation_report.txt",
            "manifest.json",
            "00_DUT_Struct_Generated.st",
            "00_Global_Variables_Generated.st",
            "01_Cylinder_Action_Generated.st",
            "02_Station_S1_Auto_Generated.st",
            "03_Station_S2_Auto_Generated.st",
            "04_Machine_Auto_Main_Generated.st",
            "HMI_Variable_List.csv",
            "IO_Mapping_List.csv",
            "Sysmac_Import_Guide.txt",
            "ST_Quality_Report.txt",
            "configs/cylinder_config.json",
            "configs/station_configs.json",
            "configs/v062_station_chain.json",
            "configs/company_symbols.json",
            "template_source/FB_Cylinder.st",
        ]

        print("\n========== 1. 必要文件检查 ==========")
        for f in required:
            if find_endswith(names, f):
                print(f"✅ {f}")
            else:
                print(f"❌ 缺少 {f}")
                ok = False

        print("\n========== 2. DUT 结构检查 ==========")
        dut_name = find_endswith(names, "00_DUT_Struct_Generated.st")
        if dut_name:
            dut = read_text(z, dut_name)
            for kw in ["TYPE", "ST_StationAuto", "ST_MachineAuto", "ST_MachineAlarm", "ST_MachineData", "ST_CylinderIO"]:
                if kw in dut:
                    print(f"✅ DUT 包含：{kw}")
                else:
                    print(f"❌ DUT 缺少：{kw}")
                    ok = False
        else:
            ok = False

        print("\n========== 3. 全局变量检查 ==========")
        gv_name = find_endswith(names, "00_Global_Variables_Generated.st")
        if gv_name:
            gv = read_text(z, gv_name)
            for kw in ["VAR_GLOBAL", "Machine_Auto", "Machine_Data", "Machine_Alarm", "Station : ARRAY", "CylinderIO", "CylinderCtrl"]:
                if kw in gv:
                    print(f"✅ 全局变量包含：{kw}")
                else:
                    print(f"❌ 全局变量缺少：{kw}")
                    ok = False
        else:
            ok = False

        print("\n========== 4. IO 映射 CSV 检查 ==========")
        io_name = find_endswith(names, "IO_Mapping_List.csv")
        if io_name:
            io_text = read_text(z, io_name)
            rows = list(csv.reader(io.StringIO(io_text)))
            print(f"✅ IO CSV 行数：{len(rows)}")
            for kw in ["Machine_Data.IN.bEstop", "Machine_Data.IN.bReset", "CylinderIO[1].bOriginSensor", "CylinderIO[1].bWorkValve"]:
                if kw in io_text:
                    print(f"✅ IO 包含：{kw}")
                else:
                    print(f"⚠️ IO 未明显包含：{kw}")
        else:
            ok = False

        print("\n========== 5. Sysmac 导入说明检查 ==========")
        guide_name = find_endswith(names, "Sysmac_Import_Guide.txt")
        if guide_name:
            guide = read_text(z, guide_name)
            for kw in ["Sysmac Studio", "导入顺序", "00_DUT_Struct_Generated.st", "00_Global_Variables_Generated.st", "IO_Mapping_List.csv"]:
                if kw in guide:
                    print(f"✅ 导入说明包含：{kw}")
                else:
                    print(f"❌ 导入说明缺少：{kw}")
                    ok = False
        else:
            ok = False

        print("\n========== 6. ST 质量报告检查 ==========")
        qr_name = find_endswith(names, "ST_Quality_Report.txt")
        if qr_name:
            qr = read_text(z, qr_name)
            for kw in ["ST Quality Report - V0.6.3", "OK:", "WARNING:", "ERROR:"]:
                if kw in qr:
                    print(f"✅ 质量报告包含：{kw}")
                else:
                    print(f"❌ 质量报告缺少：{kw}")
                    ok = False
        else:
            ok = False

        print("\n========== 7. manifest / validation 检查 ==========")
        manifest_name = find_endswith(names, "manifest.json")
        if manifest_name:
            manifest_text = read_text(z, manifest_name)
            manifest = json.loads(manifest_text)
            print("generator_version =", manifest.get("generator_version"))
            print("version =", manifest.get("version"))

            for kw in [
                "V0.6.3",
                "00_DUT_Struct_Generated.st",
                "00_Global_Variables_Generated.st",
                "IO_Mapping_List.csv",
                "Sysmac_Import_Guide.txt",
                "ST_Quality_Report.txt",
            ]:
                if kw in manifest_text:
                    print(f"✅ manifest 包含：{kw}")
                else:
                    print(f"❌ manifest 缺少：{kw}")
                    ok = False
        else:
            ok = False

        val_name = find_endswith(names, "validation_report.txt")
        if val_name:
            val_text = read_text(z, val_name)
            if "V0.6.3" in val_text:
                print("✅ validation_report 包含 V0.6.3")
            else:
                print("❌ validation_report 缺少 V0.6.3")
                ok = False
        else:
            ok = False

    print("\n========== V0.6.3 验收结论 ==========")
    if ok:
        print("✅ V0.6.3 Sysmac Studio 导入前工程规范增强通过")
    else:
        print("❌ V0.6.3 仍有问题，请把完整输出发给我")


if __name__ == "__main__":
    main()
