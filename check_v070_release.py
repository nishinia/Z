from pathlib import Path
import zipfile
import py_compile
import json

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")
APP_PRODUCT = PROJECT_DIR / "app_product.py"
RELEASE_DIR = PROJECT_DIR / "release" / "PLC_Digital_Engineer_V070"
RELEASE_ZIP = PROJECT_DIR / "release" / "PLC_Digital_Engineer_V070_Release.zip"
FINAL_PRODUCT_ZIP = PROJECT_DIR / "output" / "AI_Device_Project_Package_V070_Final.zip"
BASE_PROJECT_ZIP = PROJECT_DIR / "output" / "AI_Device_Project_Package_V06.zip"

REQUIRED_PROJECT_FILES = [
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

REQUIRED_RELEASE_FILES = [
    "app_product.py",
    "start_plc_digital_engineer_v070.bat",
    "README_PRODUCT_V070.md",
    "USER_MANUAL_V070.md",
    "RELEASE_NOTES_V070.md",
    "START_HERE.txt",
]


def find_endswith(names, suffix):
    for n in names:
        if n.replace("\\", "/").endswith(suffix):
            return n
    return None


def read_text_from_zip(z, name):
    raw = z.read(name)
    for enc in ["utf-8-sig", "utf-8", "gbk"]:
        try:
            return raw.decode(enc)
        except Exception:
            pass
    return raw.decode("utf-8", errors="ignore")


def check_project_zip(zip_path):
    ok = True

    if not zip_path.exists():
        print("❌ 工程包不存在：", zip_path)
        return False

    print("工程包：", zip_path)

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

        for f in REQUIRED_PROJECT_FILES:
            if find_endswith(names, f):
                print(f"✅ {f}")
            else:
                print(f"❌ 缺少：{f}")
                ok = False

        manifest_name = find_endswith(names, "manifest.json")
        if manifest_name:
            manifest_text = read_text_from_zip(z, manifest_name)
            manifest = json.loads(manifest_text)
            print("generator_version =", manifest.get("generator_version"))
            print("version =", manifest.get("version"))

            if "V0.6.4" in manifest_text:
                print("✅ manifest 包含 V0.6.4 核心生成器信息")
            else:
                print("❌ manifest 缺少 V0.6.4")
                ok = False

        final_name = find_endswith(names, "Final_Acceptance_Report.txt")
        if final_name:
            final_text = read_text_from_zip(z, final_name)
            if "PASS" in final_text:
                print("✅ Final_Acceptance_Report 包含 PASS")
            else:
                print("❌ Final_Acceptance_Report 缺少 PASS")
                ok = False

    return ok


def main():
    print("========== V0.7.0 最终发布验收 ==========")

    ok = True

    print("\n========== 1. app_product.py 检查 ==========")
    if APP_PRODUCT.exists():
        print("✅ app_product.py 存在")
    else:
        print("❌ app_product.py 不存在")
        return

    try:
        py_compile.compile(str(APP_PRODUCT), doraise=True)
        print("✅ app_product.py 语法检查通过")
    except Exception as e:
        print("❌ app_product.py 语法错误：", e)
        return

    app_text = APP_PRODUCT.read_text(encoding="utf-8", errors="ignore")
    for kw in ["V0.7.0", "PLC数字工程师", "AI解析整机需求", "人工确认", "最终工程包 ZIP"]:
        if kw in app_text:
            print(f"✅ 页面包含：{kw}")
        else:
            print(f"❌ 页面缺少：{kw}")
            ok = False

    print("\n========== 2. 后端生成器检查 ==========")
    try:
        from company_generators.multi_station_project_generator import generate_multi_station_project_package_from_file
        result = generate_multi_station_project_package_from_file()
        print("生成结果：", result.get("ok"))
        print("ZIP：", result.get("zip_path"))
        if not result.get("ok"):
            ok = False
    except Exception as e:
        print("❌ 后端生成器运行失败：", e)
        ok = False

    print("\n========== 3. 最终工程包 ZIP 检查 ==========")
    project_zip = FINAL_PRODUCT_ZIP if FINAL_PRODUCT_ZIP.exists() else BASE_PROJECT_ZIP
    if not check_project_zip(project_zip):
        ok = False

    print("\n========== 4. 发布目录检查 ==========")
    if RELEASE_DIR.exists():
        print("✅ 发布目录存在：", RELEASE_DIR)
    else:
        print("❌ 发布目录不存在：", RELEASE_DIR)
        ok = False

    for f in REQUIRED_RELEASE_FILES:
        p = RELEASE_DIR / f
        if p.exists():
            print(f"✅ 发布目录包含：{f}")
        else:
            print(f"❌ 发布目录缺少：{f}")
            ok = False

    for folder in ["company_generators", "configs", "company_template", "sample_output"]:
        p = RELEASE_DIR / folder
        if p.exists():
            print(f"✅ 发布目录包含：{folder}")
        else:
            print(f"❌ 发布目录缺少：{folder}")
            ok = False

    print("\n========== 5. Release ZIP 检查 ==========")
    if RELEASE_ZIP.exists():
        print("✅ Release ZIP 存在：", RELEASE_ZIP)
        print("大小 bytes：", RELEASE_ZIP.stat().st_size)
    else:
        print("❌ Release ZIP 不存在")
        ok = False

    if RELEASE_ZIP.exists():
        with zipfile.ZipFile(RELEASE_ZIP, "r") as z:
            names = z.namelist()
            for f in [
                "PLC_Digital_Engineer_V070/app_product.py",
                "PLC_Digital_Engineer_V070/start_plc_digital_engineer_v070.bat",
                "PLC_Digital_Engineer_V070/README_PRODUCT_V070.md",
                "PLC_Digital_Engineer_V070/USER_MANUAL_V070.md",
                "PLC_Digital_Engineer_V070/RELEASE_NOTES_V070.md",
            ]:
                if f in names:
                    print(f"✅ Release ZIP 包含：{f}")
                else:
                    print(f"❌ Release ZIP 缺少：{f}")
                    ok = False

    print("\n========== V0.7.0 最终验收结论 ==========")
    if ok:
        print("✅ V0.7.0 最终成品封装版验收通过")
        print("启动命令：streamlit run app_product.py")
        print("发布包：", RELEASE_ZIP)
    else:
        print("❌ V0.7.0 仍有问题，请把完整输出发给我")


if __name__ == "__main__":
    main()
