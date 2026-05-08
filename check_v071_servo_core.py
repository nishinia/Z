from pathlib import Path
import zipfile
import json
import py_compile

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")
ZIP_PATH = PROJECT_DIR / "output" / "AI_Device_Project_Package_V06.zip"
APP_PRODUCT = PROJECT_DIR / "app_product.py"

TEST_REQUIREMENT = """
项目名称：AI_Device_Project_V071_Servo。
PLC使用欧姆龙NJ501。

设备有两个气缸：
CY1 上料夹爪气缸，原点 I1_0，动点 I1_1，原点阀 Q1_0，动点阀 Q1_1。
CY2 NG剔除气缸，原点 I2_0，动点 I2_1，原点阀 Q2_0，动点阀 Q2_1。

设备有一个X轴伺服，负责搬运。
X轴需要回零。
点位1为上料位 0mm。
点位2为扫码位 120mm。
点位3为下料位 300mm。
速度 200mm/s，加速度 1000mm/s²。

S1上料工站，工站号1。
流程：等待启动后，CY1上料夹爪气缸到动点；CY1动点到位后，CY1回原点；CY1原点到位后流程完成。

S2搬运工站，工站号2。
流程：等待S1完成后，X轴先回零，再移动到上料位，夹取完成后移动到扫码位，扫码完成后移动到下料位，流程完成。

任意气缸动作超时需要报警；
伺服报警后禁止整机运行；
按复位按钮后清除报警并回到初始状态。
"""


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
    print("========== V0.7.1 伺服控制基础版验收 ==========")

    ok = True

    print("\n========== 1. 模块语法检查 ==========")
    targets = [
        PROJECT_DIR / "company_generators" / "servo_ai_parser.py",
        PROJECT_DIR / "company_generators" / "servo_generator.py",
        PROJECT_DIR / "company_generators" / "multi_station_project_generator.py",
    ]

    if APP_PRODUCT.exists():
        targets.append(APP_PRODUCT)

    for p in targets:
        try:
            py_compile.compile(str(p), doraise=True)
            print("✅ 语法通过：", p.name)
        except Exception as e:
            print("❌ 语法错误：", p, e)
            ok = False

    print("\n========== 2. AI解析测试 ==========")
    from company_generators.multi_station_ai_parser import parse_multi_station_requirement
    from company_generators.servo_ai_parser import parse_servo_requirement

    base_config = parse_multi_station_requirement(TEST_REQUIREMENT)
    axis_config = parse_servo_requirement(TEST_REQUIREMENT)
    base_config["axis_config"] = axis_config

    print("识别轴数量：", len(axis_config.get("axes", [])))
    print(json.dumps(axis_config, ensure_ascii=False, indent=2))

    if len(axis_config.get("axes", [])) >= 1:
        print("✅ 成功识别伺服轴")
    else:
        print("❌ 未识别到伺服轴")
        ok = False

    print("\n========== 3. 生成含伺服最终工程包 ==========")
    from company_generators.multi_station_project_generator import generate_multi_station_project_package

    result = generate_multi_station_project_package(
        project_info=base_config.get("project_info", {}),
        cylinder_config=base_config.get("cylinder_config", {}),
        station_configs=base_config.get("station_configs", []),
        axis_config=axis_config,
    )

    print("生成结果：", result.get("ok"))
    print("ZIP：", result.get("zip_path"))

    if not result.get("ok"):
        print("❌ 工程包生成失败")
        for e in result.get("errors", []):
            print(e)
        return

    print("\n========== 4. ZIP 伺服文件检查 ==========")
    required = [
        "00_Servo_DUT_Global_Generated.st",
        "05_Servo_Axis_Generated.st",
        "configs/axis_config.json",
        "Servo_Point_Table.csv",
        "Servo_HMI_Variable_List.csv",
        "Servo_Alarm_List.csv",
        "Servo_Debug_Guide.txt",
        "00_DUT_Struct_Generated.st",
        "00_Global_Variables_Generated.st",
        "04_Machine_Auto_Main_Generated.st",
        "Final_Acceptance_Report.txt",
    ]

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        names = z.namelist()

        for f in required:
            if find_endswith(names, f):
                print(f"✅ {f}")
            else:
                print(f"❌ 缺少：{f}")
                ok = False

        servo_st_name = find_endswith(names, "05_Servo_Axis_Generated.st")
        if servo_st_name:
            servo_text = read_text_from_zip(z, servo_st_name)
            for kw in ["Axis[1].bServoOn", "Axis[1].bHome", "Axis[1].bMoveAbs", "MC_MoveAbsolute", "Machine_Auto.bCanRun"]:
                if kw in servo_text:
                    print(f"✅ 伺服ST包含：{kw}")
                else:
                    print(f"❌ 伺服ST缺少：{kw}")
                    ok = False

        point_name = find_endswith(names, "Servo_Point_Table.csv")
        if point_name:
            point_text = read_text_from_zip(z, point_name)
            for kw in ["上料位", "扫码位", "下料位", "120", "300"]:
                if kw in point_text:
                    print(f"✅ 点位表包含：{kw}")
                else:
                    print(f"⚠️ 点位表未明显包含：{kw}")

        axis_json_name = find_endswith(names, "configs/axis_config.json")
        if axis_json_name:
            axis_text = read_text_from_zip(z, axis_json_name)
            if "X轴" in axis_text and "points" in axis_text:
                print("✅ axis_config.json 包含 X轴 和 points")
            else:
                print("❌ axis_config.json 内容不完整")
                ok = False

        manifest_name = find_endswith(names, "manifest.json")
        if manifest_name:
            manifest_text = read_text_from_zip(z, manifest_name)
            for kw in ["V0.7.1", "05_Servo_Axis_Generated.st", "Servo_Point_Table.csv"]:
                if kw in manifest_text:
                    print(f"✅ manifest 包含：{kw}")
                else:
                    print(f"❌ manifest 缺少：{kw}")
                    ok = False

    print("\n========== 5. app_product 页面接入检查 ==========")
    if APP_PRODUCT.exists():
        app_text = APP_PRODUCT.read_text(encoding="utf-8", errors="ignore")
        for kw in ["parse_servo_requirement", "Axis Config", "设备有一个X轴伺服"]:
            if kw in app_text:
                print(f"✅ app_product 包含：{kw}")
            else:
                print(f"⚠️ app_product 未明显包含：{kw}")

    print("\n========== V0.7.1 验收结论 ==========")
    if ok:
        print("✅ V0.7.1 伺服控制基础版验收通过")
    else:
        print("❌ V0.7.1 仍有问题，请把完整输出发给我")


if __name__ == "__main__":
    main()
