from pathlib import Path
from datetime import datetime
import shutil
import textwrap
import re

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")
GEN_DIR = PROJECT_DIR / "company_generators"

MULTI_GEN = GEN_DIR / "multi_station_project_generator.py"
APP_PRODUCT = PROJECT_DIR / "app_product.py"

SERVO_AI = GEN_DIR / "servo_ai_parser.py"
SERVO_GEN = GEN_DIR / "servo_generator.py"
CHECK_SCRIPT = PROJECT_DIR / "check_v071_servo_core.py"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print("✅ 写入：", path)


def backup_file(path: Path):
    if path.exists():
        backup = path.with_name(
            f"{path.stem}_backup_v071_{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}"
        )
        shutil.copy2(path, backup)
        print("✅ 备份：", backup)


def install_servo_ai_parser():
    content = r'''
import re


def _to_float(text, default=0.0):
    try:
        return float(str(text).replace(",", "").strip())
    except Exception:
        return default


def _find_default_velocity(text):
    patterns = [
        r"速度\s*([0-9]+(?:\.[0-9]+)?)\s*(?:mm/s|毫米/秒|mm每秒)?",
        r"运行速度\s*([0-9]+(?:\.[0-9]+)?)",
        r"定位速度\s*([0-9]+(?:\.[0-9]+)?)",
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return _to_float(m.group(1), 100.0)

    return 100.0


def _find_default_acc(text):
    patterns = [
        r"加速度\s*([0-9]+(?:\.[0-9]+)?)",
        r"加减速\s*([0-9]+(?:\.[0-9]+)?)",
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return _to_float(m.group(1), 500.0)

    return 500.0


def _find_points(text):
    points = []

    patterns = [
        r"点位\s*(\d+)\s*(?:为|是|:|：)?\s*([\u4e00-\u9fa5A-Za-z0-9_]+)?\s*([\-0-9]+(?:\.[0-9]+)?)\s*mm",
        r"位置\s*(\d+)\s*(?:为|是|:|：)?\s*([\u4e00-\u9fa5A-Za-z0-9_]+)?\s*([\-0-9]+(?:\.[0-9]+)?)\s*mm",
        r"P\s*(\d+)\s*(?:为|是|:|：)?\s*([\u4e00-\u9fa5A-Za-z0-9_]+)?\s*([\-0-9]+(?:\.[0-9]+)?)\s*mm",
    ]

    for pattern in patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            point_no = int(m.group(1))
            point_name = m.group(2) or f"P{point_no}"
            position = _to_float(m.group(3), 0.0)

            points.append({
                "point_no": point_no,
                "point_name": point_name,
                "position": position,
                "unit": "mm",
            })

    # 去重
    result = []
    seen = set()

    for p in sorted(points, key=lambda x: x["point_no"]):
        if p["point_no"] in seen:
            continue

        seen.add(p["point_no"])
        result.append(p)

    return result


def _find_axis_names(text):
    names = []

    # 常见写法：X轴伺服 / 一个X轴伺服 / X轴 / Y轴
    for m in re.finditer(r"([XYZUVWABC])\s*轴\s*(?:伺服|轴)?", text, re.IGNORECASE):
        axis = m.group(1).upper()
        if axis not in names:
            names.append(axis)

    # 中文描述：搬运轴、升降轴、横移轴
    chinese_axis_patterns = [
        "搬运轴",
        "升降轴",
        "横移轴",
        "旋转轴",
        "输送轴",
        "压装轴",
    ]

    for name in chinese_axis_patterns:
        if name in text and name not in names:
            names.append(name)

    return names


def parse_servo_requirement(requirement_text: str) -> dict:
    text = requirement_text or ""

    has_servo = any(k in text for k in ["伺服", "轴", "回零", "点位", "定位", "绝对位置", "MoveAbs"])

    if not has_servo:
        return {
            "axes": []
        }

    axis_names = _find_axis_names(text)

    if not axis_names:
        axis_names = ["X"]

    velocity = _find_default_velocity(text)
    acc = _find_default_acc(text)
    points = _find_points(text)

    if not points:
        points = [
            {
                "point_no": 1,
                "point_name": "上料位",
                "position": 0.0,
                "unit": "mm",
            },
            {
                "point_no": 2,
                "point_name": "工作位",
                "position": 100.0,
                "unit": "mm",
            },
        ]

    axes = []

    for i, axis_name in enumerate(axis_names, start=1):
        display_name = axis_name if str(axis_name).endswith("轴") else f"{axis_name}轴"

        axis_type = "rotary" if "旋转" in display_name else "linear"

        axes.append({
            "axis_id": f"AX{i}",
            "axis_name": display_name,
            "axis_type": axis_type,
            "unit": "deg" if axis_type == "rotary" else "mm",
            "home_required": "回零" in text or "原点" in text,
            "default_velocity": velocity,
            "default_acceleration": acc,
            "default_deceleration": acc,
            "positive_limit": "",
            "negative_limit": "",
            "home_sensor": "",
            "servo_alarm": "",
            "points": points,
            "sequence": [
                "ServoOn",
                "Home",
                "MoveAbs",
                "Done",
            ],
        })

    return {
        "axes": axes
    }
'''
    write_file(SERVO_AI, content)


def install_servo_generator():
    content = r'''
import csv
import io
import re
from datetime import datetime


def normalize_axis_config(axis_config):
    axes = []

    for i, axis in enumerate((axis_config or {}).get("axes", []), start=1):
        if not isinstance(axis, dict):
            continue

        axis_id = axis.get("axis_id") or axis.get("id") or f"AX{i}"
        axis_name = axis.get("axis_name") or axis.get("name") or f"{axis_id}轴"

        points = axis.get("points", [])
        if not isinstance(points, list):
            points = []

        axes.append({
            "index": i,
            "axis_id": str(axis_id),
            "axis_name": str(axis_name),
            "axis_type": axis.get("axis_type", "linear"),
            "unit": axis.get("unit", "mm"),
            "home_required": bool(axis.get("home_required", True)),
            "default_velocity": float(axis.get("default_velocity", 100.0) or 100.0),
            "default_acceleration": float(axis.get("default_acceleration", 500.0) or 500.0),
            "default_deceleration": float(axis.get("default_deceleration", 500.0) or 500.0),
            "points": points,
            "raw": axis,
        })

    return axes


def generate_servo_dut_global_st(axis_config):
    axes = normalize_axis_config(axis_config)
    axis_count = max(len(axes), 1)
    max_points = max([len(a["points"]) for a in axes], default=1)
    max_points = max(max_points, 1)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("(*")
    lines.append("================================================================================")
    lines.append(" File    : 00_Servo_DUT_Global_Generated.st")
    lines.append(" Version : V0.7.1")
    lines.append(" Purpose : 伺服轴 DUT / 全局变量建议")
    lines.append(f" Time    : {now}")
    lines.append("================================================================================")
    lines.append("*)")
    lines.append("")
    lines.append("TYPE")
    lines.append("    ST_AxisAuto : STRUCT")
    lines.append("        bServoOn        : BOOL;")
    lines.append("        bHome           : BOOL;")
    lines.append("        bHomeDone       : BOOL;")
    lines.append("        bJogPositive    : BOOL;")
    lines.append("        bJogNegative    : BOOL;")
    lines.append("        bMoveAbs        : BOOL;")
    lines.append("        bMoveRel        : BOOL;")
    lines.append("        bStop           : BOOL;")
    lines.append("        bReset          : BOOL;")
    lines.append("        bBusy           : BOOL;")
    lines.append("        bDone           : BOOL;")
    lines.append("        bAlarm          : BOOL;")
    lines.append("        nAlarmNo        : INT;")
    lines.append("        rActualPosition : LREAL;")
    lines.append("        rTargetPosition : LREAL;")
    lines.append("        rVelocity       : LREAL;")
    lines.append("        rAcceleration   : LREAL;")
    lines.append("        rDeceleration   : LREAL;")
    lines.append("    END_STRUCT;")
    lines.append("")
    lines.append("    ST_AxisPoint : STRUCT")
    lines.append("        nPointNo  : INT;")
    lines.append("        sPointName : STRING[32];")
    lines.append("        rPosition : LREAL;")
    lines.append("        rVelocity : LREAL;")
    lines.append("    END_STRUCT;")
    lines.append("END_TYPE")
    lines.append("")
    lines.append("VAR_GLOBAL")
    lines.append(f"    Axis      : ARRAY[1..{axis_count}] OF ST_AxisAuto;")
    lines.append(f"    AxisPoint : ARRAY[1..{axis_count}, 1..{max_points}] OF ST_AxisPoint;")
    lines.append("END_VAR")
    lines.append("")
    lines.append("(*")
    lines.append("轴索引：")
    for axis in axes:
        lines.append(f"- Axis[{axis['index']}] = {axis['axis_id']} / {axis['axis_name']}")
    lines.append("*)")
    lines.append("")

    return "\n".join(lines)


def generate_servo_axis_st(axis_config):
    axes = normalize_axis_config(axis_config)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("(*")
    lines.append("================================================================================")
    lines.append(" File    : 05_Servo_Axis_Generated.st")
    lines.append(" Version : V0.7.1")
    lines.append(" Purpose : 伺服轴基础控制逻辑建议")
    lines.append(f" Time    : {now}")
    lines.append("================================================================================")
    lines.append("*)")
    lines.append("")
    lines.append("// 注意：以下为伺服控制逻辑框架。")
    lines.append("// 正式使用前需要在 Sysmac Studio 中绑定真实 Axis 轴对象，")
    lines.append("// 并由 PLC 工程师替换为 MC_Power / MC_Home / MC_MoveAbsolute / MC_Stop 等真实运动控制指令。")
    lines.append("")

    for axis in axes:
        idx = axis["index"]
        name = axis["axis_name"]
        vel = axis["default_velocity"]
        acc = axis["default_acceleration"]
        dec = axis["default_deceleration"]

        lines.append("// ================================================================")
        lines.append(f"// Axis[{idx}] - {name}")
        lines.append("// ================================================================")
        lines.append(f"Axis[{idx}].rVelocity := {vel};")
        lines.append(f"Axis[{idx}].rAcceleration := {acc};")
        lines.append(f"Axis[{idx}].rDeceleration := {dec};")
        lines.append("")
        lines.append(f"IF Machine_Data.IN.bReset THEN")
        lines.append(f"    Axis[{idx}].bReset := TRUE;")
        lines.append(f"    Axis[{idx}].bAlarm := FALSE;")
        lines.append(f"    Axis[{idx}].nAlarmNo := 0;")
        lines.append(f"    Axis[{idx}].bDone := FALSE;")
        lines.append(f"    Axis[{idx}].bBusy := FALSE;")
        lines.append(f"END_IF;")
        lines.append("")
        lines.append(f"// 伺服报警时禁止整机运行")
        lines.append(f"IF Axis[{idx}].bAlarm THEN")
        lines.append(f"    Machine_Auto.bCanRun := FALSE;")
        lines.append(f"    Machine_Auto.bAnyStationAlarm := TRUE;")
        lines.append(f"END_IF;")
        lines.append("")
        lines.append(f"// Servo On 框架")
        lines.append(f"IF Axis[{idx}].bServoOn AND NOT Axis[{idx}].bAlarm THEN")
        lines.append(f"    // TODO: 调用 MC_Power")
        lines.append(f"END_IF;")
        lines.append("")
        lines.append(f"// Home 框架")
        lines.append(f"IF Axis[{idx}].bHome AND NOT Axis[{idx}].bAlarm THEN")
        lines.append(f"    Axis[{idx}].bBusy := TRUE;")
        lines.append(f"    // TODO: 调用 MC_Home")
        lines.append(f"    // Home 完成后：Axis[{idx}].bHomeDone := TRUE;")
        lines.append(f"END_IF;")
        lines.append("")
        lines.append(f"// Move Absolute 框架")
        lines.append(f"IF Axis[{idx}].bMoveAbs AND Axis[{idx}].bHomeDone AND NOT Axis[{idx}].bAlarm THEN")
        lines.append(f"    Axis[{idx}].bBusy := TRUE;")
        lines.append(f"    // TODO: 调用 MC_MoveAbsolute")
        lines.append(f"    // Position := Axis[{idx}].rTargetPosition")
        lines.append(f"    // Velocity := Axis[{idx}].rVelocity")
        lines.append(f"END_IF;")
        lines.append("")
        lines.append(f"// Jog Positive / Negative 框架")
        lines.append(f"IF Axis[{idx}].bJogPositive AND NOT Axis[{idx}].bAlarm THEN")
        lines.append(f"    // TODO: 调用 MC_MoveVelocity 正方向")
        lines.append(f"END_IF;")
        lines.append("")
        lines.append(f"IF Axis[{idx}].bJogNegative AND NOT Axis[{idx}].bAlarm THEN")
        lines.append(f"    // TODO: 调用 MC_MoveVelocity 负方向")
        lines.append(f"END_IF;")
        lines.append("")
        lines.append(f"// Stop 框架")
        lines.append(f"IF Axis[{idx}].bStop OR Machine_Data.IN.bEstop THEN")
        lines.append(f"    // TODO: 调用 MC_Stop / MC_Halt")
        lines.append(f"    Axis[{idx}].bBusy := FALSE;")
        lines.append(f"END_IF;")
        lines.append("")

    if not axes:
        lines.append("// 当前未识别到伺服轴。")
        lines.append("")

    return "\n".join(lines)


def generate_servo_point_table_csv_bytes(axis_config):
    axes = normalize_axis_config(axis_config)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "axis_index",
        "axis_id",
        "axis_name",
        "point_no",
        "point_name",
        "position",
        "unit",
        "velocity",
        "description",
    ])

    for axis in axes:
        for p in axis["points"]:
            point_no = p.get("point_no", "")
            point_name = p.get("point_name", f"P{point_no}")
            position = p.get("position", 0)
            unit = p.get("unit", axis["unit"])
            velocity = p.get("velocity", axis["default_velocity"])

            writer.writerow([
                axis["index"],
                axis["axis_id"],
                axis["axis_name"],
                point_no,
                point_name,
                position,
                unit,
                velocity,
                f"{axis['axis_name']} 点位 {point_name}",
            ])

    return output.getvalue().encode("utf-8-sig")


def generate_servo_hmi_variable_csv_bytes(axis_config):
    axes = normalize_axis_config(axis_config)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "category",
        "variable",
        "chinese_name",
        "data_type",
        "access",
        "description",
    ])

    for axis in axes:
        idx = axis["index"]
        name = axis["axis_name"]

        rows = [
            [name, f"Axis[{idx}].bServoOn", f"{name} 伺服使能", "BOOL", "ReadWrite", "HMI伺服使能命令"],
            [name, f"Axis[{idx}].bHome", f"{name} 回零命令", "BOOL", "ReadWrite", "HMI回零命令"],
            [name, f"Axis[{idx}].bHomeDone", f"{name} 回零完成", "BOOL", "Read", "轴回零完成状态"],
            [name, f"Axis[{idx}].bJogPositive", f"{name} 正向点动", "BOOL", "ReadWrite", "HMI正向点动"],
            [name, f"Axis[{idx}].bJogNegative", f"{name} 反向点动", "BOOL", "ReadWrite", "HMI反向点动"],
            [name, f"Axis[{idx}].bMoveAbs", f"{name} 绝对定位", "BOOL", "ReadWrite", "HMI绝对定位命令"],
            [name, f"Axis[{idx}].bStop", f"{name} 停止", "BOOL", "ReadWrite", "HMI停止命令"],
            [name, f"Axis[{idx}].bBusy", f"{name} 运行中", "BOOL", "Read", "轴运行中"],
            [name, f"Axis[{idx}].bDone", f"{name} 完成", "BOOL", "Read", "轴动作完成"],
            [name, f"Axis[{idx}].bAlarm", f"{name} 报警", "BOOL", "Read", "轴报警"],
            [name, f"Axis[{idx}].nAlarmNo", f"{name} 报警号", "INT", "Read", "轴报警编号"],
            [name, f"Axis[{idx}].rActualPosition", f"{name} 实际位置", "LREAL", "Read", "轴实际位置"],
            [name, f"Axis[{idx}].rTargetPosition", f"{name} 目标位置", "LREAL", "ReadWrite", "轴目标位置"],
            [name, f"Axis[{idx}].rVelocity", f"{name} 速度", "LREAL", "ReadWrite", "轴速度"],
        ]

        for row in rows:
            writer.writerow(row)

    return output.getvalue().encode("utf-8-sig")


def generate_servo_alarm_list_csv_bytes(axis_config):
    axes = normalize_axis_config(axis_config)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "alarm_no",
        "level",
        "axis_id",
        "axis_name",
        "alarm_name",
        "trigger_condition",
        "reset_method",
        "hmi_message",
    ])

    for axis in axes:
        idx = axis["index"]
        base = 4000 + idx * 100

        rows = [
            [base + 1, "Error", axis["axis_id"], axis["axis_name"], "伺服报警", f"Axis[{idx}].bAlarm = TRUE", "排除伺服故障后复位", f"{axis['axis_name']} 伺服报警"],
            [base + 2, "Error", axis["axis_id"], axis["axis_name"], "未回零禁止定位", f"Axis[{idx}].bMoveAbs = TRUE AND Axis[{idx}].bHomeDone = FALSE", "先执行回零", f"{axis['axis_name']} 未回零，禁止定位"],
            [base + 3, "Error", axis["axis_id"], axis["axis_name"], "轴运动超时", f"Axis[{idx}].bBusy 超时", "检查机械阻力、限位、驱动器", f"{axis['axis_name']} 运动超时"],
            [base + 4, "Warning", axis["axis_id"], axis["axis_name"], "急停轴停止", "Machine_Data.IN.bEstop = TRUE", "解除急停后复位", f"{axis['axis_name']} 急停停止"],
        ]

        for row in rows:
            writer.writerow(row)

    return output.getvalue().encode("utf-8-sig")


def generate_servo_debug_guide_txt(axis_config):
    axes = normalize_axis_config(axis_config)

    lines = []
    lines.append("Servo Debug Guide - V0.7.1")
    lines.append("=" * 80)
    lines.append("")
    lines.append("一、调试前确认")
    lines.append("1. 确认伺服驱动器参数已正确设置。")
    lines.append("2. 确认正负限位、原点信号、急停、安全回路有效。")
    lines.append("3. 确认机械机构无干涉。")
    lines.append("4. 首次运行必须低速点动。")
    lines.append("")
    lines.append("二、推荐调试顺序")
    lines.append("1. Servo On")
    lines.append("2. 正反向点动，确认方向")
    lines.append("3. 回零")
    lines.append("4. 小距离绝对定位")
    lines.append("5. 点位表逐点验证")
    lines.append("6. 与气缸/工站流程联动")
    lines.append("7. 急停和报警复位测试")
    lines.append("")
    lines.append("三、当前轴清单")

    if axes:
        for axis in axes:
            lines.append(f"- Axis[{axis['index']}] {axis['axis_id']} / {axis['axis_name']}")
            for p in axis["points"]:
                lines.append(f"  - P{p.get('point_no')}: {p.get('point_name')} = {p.get('position')} {p.get('unit', axis['unit'])}")
    else:
        lines.append("未识别到伺服轴。")

    lines.append("")
    lines.append("四、重要说明")
    lines.append("本版本生成的是伺服控制框架，不替代真实运动控制调试。")
    lines.append("需要 PLC 工程师在 Sysmac Studio 中绑定真实 Axis 变量，并接入 MC_Power、MC_Home、MC_MoveAbsolute、MC_Stop 等运动控制指令。")
    lines.append("")

    return "\n".join(lines)
'''
    write_file(SERVO_GEN, content)


def patch_multi_station_generator():
    if not MULTI_GEN.exists():
        print("❌ 找不到：", MULTI_GEN)
        return False

    backup_file(MULTI_GEN)

    text = MULTI_GEN.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")
    ok = True

    if 'GENERATOR_VERSION = "V0.7.1"' not in text:
        text = re.sub(
            r'GENERATOR_VERSION\s*=\s*"[^"]+"',
            'GENERATOR_VERSION = "V0.7.1"',
            text,
            count=1,
        )
        print("✅ 版本号升级为 V0.7.1")

    if "company_generators.servo_generator" not in text:
        marker = "\n\nGENERATOR_NAME ="
        import_block = '''
from company_generators.servo_generator import (
    normalize_axis_config,
    generate_servo_dut_global_st,
    generate_servo_axis_st,
    generate_servo_point_table_csv_bytes,
    generate_servo_hmi_variable_csv_bytes,
    generate_servo_alarm_list_csv_bytes,
    generate_servo_debug_guide_txt
)
'''
        if marker in text:
            text = text.replace(marker, "\n\n" + import_block + "\nGENERATOR_NAME =", 1)
            print("✅ 增加 servo_generator import")
        else:
            print("❌ 找不到 import 插入点")
            ok = False
    else:
        print("✅ servo_generator import 已存在")

    # 修改函数签名，增加 axis_config
    old_sig = '''def generate_multi_station_project_package(
    project_info: dict,
    cylinder_config: dict,
    station_configs: list[dict],
    package_dir: Path = PACKAGE_DIR,
    zip_path: Path = ZIP_PATH
) -> dict:
'''
    new_sig = '''def generate_multi_station_project_package(
    project_info: dict,
    cylinder_config: dict,
    station_configs: list[dict],
    axis_config: dict | None = None,
    package_dir: Path = PACKAGE_DIR,
    zip_path: Path = ZIP_PATH
) -> dict:
'''
    if old_sig in text:
        text = text.replace(old_sig, new_sig, 1)
        print("✅ generate_multi_station_project_package 增加 axis_config 参数")
    elif "axis_config: dict | None = None" in text:
        print("✅ 函数签名已包含 axis_config")
    else:
        print("⚠️ 未找到标准函数签名，跳过签名修改")

    if "axis_config = axis_config or" not in text:
        marker = '''    if errors:
        return {
            "ok": False,
            "errors": errors,
            "warnings": warnings,
            "package_dir": None,
            "zip_path": None,
            "files": []
        }

'''
        insert = '''    axis_config = axis_config or {"axes": []}
    normalized_axes = normalize_axis_config(axis_config)

'''
        if marker in text:
            text = text.replace(marker, marker + insert, 1)
            print("✅ 增加 axis_config 初始化")
        else:
            print("❌ 找不到 axis_config 初始化插入点")
            ok = False
    else:
        print("✅ axis_config 初始化已存在")

    # 插入伺服文件生成逻辑
    if 'servo_axis_path = package_dir / "05_Servo_Axis_Generated.st"' not in text:
        marker = '''    configs_dir = package_dir / "configs"
'''
        insert = '''    # V0.7.1：伺服轴控制基础文件
    if normalized_axes:
        servo_dut_global_path = package_dir / "00_Servo_DUT_Global_Generated.st"
        write_text(servo_dut_global_path, generate_servo_dut_global_st(axis_config))
        files_written.append((servo_dut_global_path, "generated_st"))

        servo_axis_path = package_dir / "05_Servo_Axis_Generated.st"
        write_text(servo_axis_path, generate_servo_axis_st(axis_config))
        files_written.append((servo_axis_path, "generated_st"))

        servo_point_table_path = package_dir / "Servo_Point_Table.csv"
        write_bytes(servo_point_table_path, generate_servo_point_table_csv_bytes(axis_config))
        files_written.append((servo_point_table_path, "servo_point_table"))

        servo_hmi_path = package_dir / "Servo_HMI_Variable_List.csv"
        write_bytes(servo_hmi_path, generate_servo_hmi_variable_csv_bytes(axis_config))
        files_written.append((servo_hmi_path, "hmi_variable"))

        servo_alarm_path = package_dir / "Servo_Alarm_List.csv"
        write_bytes(servo_alarm_path, generate_servo_alarm_list_csv_bytes(axis_config))
        files_written.append((servo_alarm_path, "alarm_list"))

        servo_debug_guide_path = package_dir / "Servo_Debug_Guide.txt"
        write_text(servo_debug_guide_path, generate_servo_debug_guide_txt(axis_config))
        files_written.append((servo_debug_guide_path, "document"))

'''
        if marker in text:
            text = text.replace(marker, insert + marker, 1)
            print("✅ 接入伺服轴生成文件")
        else:
            print("❌ 找不到 configs_dir 插入点")
            ok = False
    else:
        print("✅ 伺服轴生成逻辑已存在")

    # 写 axis_config.json
    if 'axis_config_path = configs_dir / "axis_config.json"' not in text:
        marker = '''    write_text(
        station_configs_path,
        json.dumps(station_configs, ensure_ascii=False, indent=4)
    )

'''
        insert = '''    axis_config_path = configs_dir / "axis_config.json"
    write_text(
        axis_config_path,
        json.dumps(axis_config, ensure_ascii=False, indent=4)
    )

'''
        if marker in text:
            text = text.replace(marker, marker + insert, 1)
            print("✅ 写入 configs/axis_config.json")
        else:
            print("❌ 找不到 station_configs 写入点")
            ok = False
    else:
        print("✅ axis_config.json 写入逻辑已存在")

    if '(axis_config_path, "config")' not in text:
        # 在 files_written.extend 的 config 列表中加 axis_config
        text = text.replace(
            '(v062_station_chain_path, "config")',
            '(v062_station_chain_path, "config"),\n        (axis_config_path, "config")',
            1,
        )
        print("✅ axis_config.json 加入 files_written")

    # manifest 增强
    if '"v071_features"' not in text:
        marker = '''    manifest_path = package_dir / "manifest.json"
'''
        insert = '''    # V0.7.1：伺服轴 manifest 增强信息
    manifest["version"] = GENERATOR_VERSION
    manifest["v071_generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    manifest["v071_servo_axis_count"] = len(normalized_axes)
    manifest["v071_features"] = [
        "伺服轴中文需求解析接入",
        "伺服轴控制 ST 框架生成",
        "伺服轴 DUT / 全局变量建议生成",
        "伺服点位表生成",
        "伺服 HMI 变量清单生成",
        "伺服报警清单生成",
        "伺服调试说明生成"
    ]
    manifest["v071_added_files"] = [
        "00_Servo_DUT_Global_Generated.st",
        "05_Servo_Axis_Generated.st",
        "configs/axis_config.json",
        "Servo_Point_Table.csv",
        "Servo_HMI_Variable_List.csv",
        "Servo_Alarm_List.csv",
        "Servo_Debug_Guide.txt"
    ]

'''
        if marker in text:
            text = text.replace(marker, insert + marker, 1)
            print("✅ manifest 增强 V0.7.1")
        else:
            print("❌ 找不到 manifest 插入点")
            ok = False
    else:
        print("✅ manifest V0.7.1 已存在")

    # validation 增强
    if "V0.7.1 伺服控制基础版" not in text:
        marker = '''    readme_path = package_dir / "00_README.txt"
'''
        insert = '''    if normalized_axes:
        validation_text += (
            "\\n\\n========== V0.7.1 伺服控制基础版 ==========\\n"
            "✅ 已识别伺服轴配置 axis_config\\n"
            "✅ 已生成 00_Servo_DUT_Global_Generated.st\\n"
            "✅ 已生成 05_Servo_Axis_Generated.st\\n"
            "✅ 已生成 Servo_Point_Table.csv\\n"
            "✅ 已生成 Servo_HMI_Variable_List.csv\\n"
            "✅ 已生成 Servo_Alarm_List.csv\\n"
            "✅ 已生成 Servo_Debug_Guide.txt\\n"
        )
    else:
        validation_text += (
            "\\n\\n========== V0.7.1 伺服控制基础版 ==========\\n"
            "ℹ️ 当前需求未识别到伺服轴，未生成伺服控制文件。\\n"
        )

'''
        if marker in text:
            text = text.replace(marker, insert + marker, 1)
            print("✅ validation_report 增强 V0.7.1")
        else:
            print("❌ 找不到 validation 插入点")
            ok = False
    else:
        print("✅ validation V0.7.1 已存在")

    # from_file 传 axis_config
    if "axis_config = config.get(\"axis_config\"" not in text:
        marker = '''    station_configs = config.get("station_configs", [])
'''
        insert = '''    axis_config = config.get("axis_config", {"axes": []})
'''
        if marker in text:
            text = text.replace(marker, marker + insert, 1)
            print("✅ from_file 读取 axis_config")
        else:
            print("⚠️ 未找到 from_file station_configs 行")

    old_call = '''        station_configs=station_configs
    )
'''
    new_call = '''        station_configs=station_configs,
        axis_config=axis_config
    )
'''
    if "axis_config=axis_config" not in text and old_call in text:
        text = text.replace(old_call, new_call, 1)
        print("✅ from_file 调用传入 axis_config")

    MULTI_GEN.write_text(text, encoding="utf-8")

    if ok:
        print("✅ multi_station_project_generator.py 已升级到 V0.7.1")
    else:
        print("❌ multi_station_project_generator.py 部分升级失败，请把输出发给我")

    return ok


def patch_app_product():
    if not APP_PRODUCT.exists():
        print("⚠️ 未找到 app_product.py，跳过页面接入")
        return True

    backup_file(APP_PRODUCT)

    text = APP_PRODUCT.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")

    if "servo_ai_parser" not in text:
        marker = "from company_generators.multi_station_ai_parser import parse_multi_station_requirement\n"
        insert = "from company_generators.servo_ai_parser import parse_servo_requirement\n"
        if marker in text:
            text = text.replace(marker, marker + insert, 1)
            print("✅ app_product 增加伺服解析 import")
        else:
            print("⚠️ app_product 未找到 import 插入点")

    if 'CORE_VERSION = "V0.7.1"' not in text:
        text = re.sub(r'CORE_VERSION\s*=\s*"[^"]+"', 'CORE_VERSION = "V0.7.1"', text, count=1)
        print("✅ app_product CORE_VERSION → V0.7.1")

    # 默认需求增加伺服样例
    if "设备有一个X轴伺服" not in text:
        old = '''任意气缸动作超时需要报警；
按复位按钮后清除报警并回到初始状态。
"""'''
        new = '''任意气缸动作超时需要报警；
按复位按钮后清除报警并回到初始状态。

设备有一个X轴伺服，负责搬运。
X轴需要回零。
点位1为上料位 0mm。
点位2为扫码位 120mm。
点位3为下料位 300mm。
速度 200mm/s，加速度 1000mm/s²。
启动后先回零，再移动到上料位，夹取完成后移动到扫码位，扫码完成后移动到下料位。
伺服报警后禁止整机运行，复位后允许重新回零。
"""'''
        if old in text:
            text = text.replace(old, new, 1)
            print("✅ app_product 默认需求增加伺服样例")
        else:
            print("⚠️ 未找到默认需求插入点")

    # 解析后合并 axis_config
    if 'servo_axis_config = parse_servo_requirement(requirement_text)' not in text:
        old = '''            parsed_config = parse_multi_station_requirement(requirement_text)

        st.session_state["v065_config"] = parsed_config
'''
        new = '''            parsed_config = parse_multi_station_requirement(requirement_text)
            servo_axis_config = parse_servo_requirement(requirement_text)
            parsed_config["axis_config"] = servo_axis_config

        st.session_state["v065_config"] = parsed_config
'''
        if old in text:
            text = text.replace(old, new, 1)
            print("✅ app_product 解析时合并 axis_config")
        else:
            print("⚠️ 未找到解析插入点")

    # 生成时传 axis_config
    if "axis_config=config.get(\"axis_config\"" not in text:
        old = '''                    station_configs=station_configs,
                )
'''
        new = '''                    station_configs=station_configs,
                    axis_config=config.get("axis_config", {"axes": []}),
                )
'''
        if old in text:
            text = text.replace(old, new, 1)
            print("✅ app_product 生成时传 axis_config")
        else:
            print("⚠️ 未找到生成调用插入点")

    # 增加 Axis Config tab
    if '"Axis Config"' not in text:
        old = '''    tab_project, tab_cylinder, tab_station, tab_json = st.tabs([
        "Project Info",
        "Cylinder Config",
        "Station Configs",
        "完整JSON",
    ])
'''
        new = '''    tab_project, tab_cylinder, tab_station, tab_axis, tab_json = st.tabs([
        "Project Info",
        "Cylinder Config",
        "Station Configs",
        "Axis Config",
        "完整JSON",
    ])
'''
        if old in text:
            text = text.replace(old, new, 1)
            print("✅ app_product 增加 Axis Config tab")

        old2 = '''    with tab_station:
        st.code(
            json.dumps(config.get("station_configs", []), ensure_ascii=False, indent=4),
            language="json",
        )

    with tab_json:
'''
        new2 = '''    with tab_station:
        st.code(
            json.dumps(config.get("station_configs", []), ensure_ascii=False, indent=4),
            language="json",
        )

    with tab_axis:
        st.code(
            json.dumps(config.get("axis_config", {"axes": []}), ensure_ascii=False, indent=4),
            language="json",
        )

    with tab_json:
'''
        if old2 in text:
            text = text.replace(old2, new2, 1)
            print("✅ app_product 显示 Axis Config")

    APP_PRODUCT.write_text(text, encoding="utf-8")
    print("✅ app_product.py 已接入伺服解析和显示")

    return True


def install_check_script():
    content = r'''
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
'''
    write_file(CHECK_SCRIPT, content)


def main():
    print("========== 安装 V0.7.1 Servo Core ==========")

    if not PROJECT_DIR.exists():
        print("❌ 项目目录不存在：", PROJECT_DIR)
        return

    if not GEN_DIR.exists():
        print("❌ company_generators 目录不存在：", GEN_DIR)
        return

    install_servo_ai_parser()
    install_servo_generator()
    patch_multi_station_generator()
    patch_app_product()
    install_check_script()

    print("\n========== 安装结果 ==========")
    print("✅ V0.7.1 伺服控制基础版安装完成")
    print("下一步运行：")
    print("python check_v071_servo_core.py")


if __name__ == "__main__":
    main()