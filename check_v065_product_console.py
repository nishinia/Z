from pathlib import Path
import py_compile
import zipfile
import json

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")
APP_PRODUCT = PROJECT_DIR / "app_product.py"
ZIP_PATH = PROJECT_DIR / "output" / "AI_Device_Project_Package_V06.zip"

REQUIRED_APP_KEYWORDS = [
    "PLC数字工程师成品版操作台",
    "AI解析整机需求",
    "人工确认",
    "生成 V0.6.5 最终工程包 ZIP",
    "下载 V0.6.5 最终工程包 ZIP",
]

REQUIRED_ZIP_FILES = [
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


def read_text_from_zip(z, name):
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
    print("========== V0.6.5 成品版操作台验收 ==========")

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

    for kw in REQUIRED_APP_KEYWORDS:
        if kw in app_text:
            print(f"✅ 页面包含：{kw}")
        else:
            print(f"❌ 页面缺少：{kw}")
            ok = False

    print("\n========== 2. 后端生成器自动生成测试 ==========")
    from company_generators.multi_station_project_generator import generate_multi_station_project_package_from_file

    result = generate_multi_station_project_package_from_file()
    print("生成结果：", result.get("ok"))
    print("ZIP：", result.get("zip_path"))

    if not result.get("ok"):
        print("❌ 后端工程包生成失败")
        for e in result.get("errors", []):
            print(e)
        return

    if not ZIP_PATH.exists():
        print("❌ ZIP 不存在：", ZIP_PATH)
        return

    print("\n========== 3. ZIP 最终交付物检查 ==========")
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        names = z.namelist()

        for f in REQUIRED_ZIP_FILES:
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

    print("\n========== V0.6.5 验收结论 ==========")
    if ok:
        print("✅ V0.6.5 成品版操作台验收通过")
        print("启动命令：streamlit run app_product.py")
    else:
        print("❌ V0.6.5 仍有问题，请把完整输出发给我")


if __name__ == "__main__":
    main()
