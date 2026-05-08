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
