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
    print("========== V0.6.4 自动生成工程包 ==========")

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

    print("\n========== V0.6.4 ZIP 检查 ==========")
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
            "IO_Mapping_Enhanced.csv",
            "Alarm_List.csv",
            "Step_List.csv",
            "Variable_CrossReference_Report.txt",
            "Final_Acceptance_Report.txt",
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

        print("\n========== 2. Alarm_List.csv 检查 ==========")
        alarm_name = find_endswith(names, "Alarm_List.csv")
        if alarm_name:
            alarm_text = read_text(z, alarm_name)
            rows = list(csv.reader(io.StringIO(alarm_text)))
            print(f"✅ Alarm CSV 行数：{len(rows)}")
            for kw in ["alarm_no", "整机急停", "安全回路异常", "气源异常"]:
                if kw in alarm_text:
                    print(f"✅ Alarm 包含：{kw}")
                else:
                    print(f"⚠️ Alarm 未明显包含：{kw}")
        else:
            ok = False

        print("\n========== 3. Step_List.csv 检查 ==========")
        step_name = find_endswith(names, "Step_List.csv")
        if step_name:
            step_text = read_text(z, step_name)
            rows = list(csv.reader(io.StringIO(step_text)))
            print(f"✅ Step CSV 行数：{len(rows)}")
            for kw in ["station_id", "step_no", "action", "timeout_ms"]:
                if kw in step_text:
                    print(f"✅ Step 包含：{kw}")
                else:
                    print(f"❌ Step 缺少：{kw}")
                    ok = False
        else:
            ok = False

        print("\n========== 4. IO_Mapping_Enhanced.csv 检查 ==========")
        io_name = find_endswith(names, "IO_Mapping_Enhanced.csv")
        if io_name:
            io_text = read_text(z, io_name)
            rows = list(csv.reader(io.StringIO(io_text)))
            print(f"✅ Enhanced IO CSV 行数：{len(rows)}")
            for kw in ["parsed_io_type", "channel", "CylinderIO[1].bOriginSensor", "CylinderIO[1].bWorkValve"]:
                if kw in io_text:
                    print(f"✅ Enhanced IO 包含：{kw}")
                else:
                    print(f"⚠️ Enhanced IO 未明显包含：{kw}")
        else:
            ok = False

        print("\n========== 5. 变量交叉引用报告检查 ==========")
        cross_name = find_endswith(names, "Variable_CrossReference_Report.txt")
        if cross_name:
            cross_text = read_text(z, cross_name)
            for kw in ["Variable Cross Reference Report - V0.6.4", "变量引用统计", "Machine_Auto", "Station", "PASS"]:
                if kw in cross_text:
                    print(f"✅ 变量报告包含：{kw}")
                else:
                    print(f"❌ 变量报告缺少：{kw}")
                    ok = False
        else:
            ok = False

        print("\n========== 6. 最终验收报告检查 ==========")
        final_name = find_endswith(names, "Final_Acceptance_Report.txt")
        if final_name:
            final_text = read_text(z, final_name)
            for kw in ["Final Acceptance Report - V0.6.4", "交付文件检查", "V0.6.4 新增交付物", "PASS"]:
                if kw in final_text:
                    print(f"✅ 最终报告包含：{kw}")
                else:
                    print(f"❌ 最终报告缺少：{kw}")
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
                "V0.6.4",
                "Alarm_List.csv",
                "Step_List.csv",
                "IO_Mapping_Enhanced.csv",
                "Variable_CrossReference_Report.txt",
                "Final_Acceptance_Report.txt",
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
            if "V0.6.4" in val_text:
                print("✅ validation_report 包含 V0.6.4")
            else:
                print("❌ validation_report 缺少 V0.6.4")
                ok = False
        else:
            ok = False

    print("\n========== V0.6.4 验收结论 ==========")
    if ok:
        print("✅ V0.6.4 工程质量增强通过")
    else:
        print("❌ V0.6.4 仍有问题，请把完整输出发给我")


if __name__ == "__main__":
    main()
