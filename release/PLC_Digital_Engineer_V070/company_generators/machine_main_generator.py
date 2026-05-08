from datetime import datetime
import re


def natural_station_index(station_id, fallback):
    text = str(station_id)
    nums = re.findall(r"\d+", text)
    if nums:
        return int(nums[-1])
    return fallback


def normalize_station_configs(station_configs):
    result = []

    for i, cfg in enumerate(station_configs, start=1):
        if not isinstance(cfg, dict):
            continue

        sid = (
            cfg.get("station_id")
            or cfg.get("id")
            or cfg.get("station")
            or f"S{i}"
        )

        sid = str(sid).upper().replace("STATION_", "S").replace("STATION", "S")

        if not sid.startswith("S"):
            sid = f"S{i}"

        station_name = (
            cfg.get("station_name")
            or cfg.get("name")
            or cfg.get("title")
            or f"{sid}工站"
        )

        result.append({
            "station_id": sid,
            "station_name": station_name,
            "raw": cfg,
        })

    result.sort(key=lambda x: natural_station_index(x["station_id"], 999))
    return result


def generate_machine_main_st(station_configs):
    stations = normalize_station_configs(station_configs)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []

    lines.append("(*")
    lines.append("================================================================================")
    lines.append(" File    : 04_Machine_Auto_Main_Generated.st")
    lines.append(" Version : V0.6.2.1")
    lines.append(" Author  : PLC Digital Engineer AI")
    lines.append(f" Time    : {now}")
    lines.append("")
    lines.append(" Purpose : 整机主流程 / 多工站互锁 / 报警汇总 / 统一复位")
    lines.append("================================================================================")
    lines.append("*)")
    lines.append("")

    lines.append("// ================================================================")
    lines.append("// 1. 整机基础运行条件")
    lines.append("// ================================================================")
    lines.append("Machine_Auto.bReady := Machine_Data.IN.bSafety")
    lines.append("                       AND Machine_Data.IN.bAirOn")
    lines.append("                       AND NOT Machine_Data.IN.bEstop;")
    lines.append("")

    alarm_exprs = []
    for i, st in enumerate(stations, start=1):
        idx = natural_station_index(st["station_id"], i)
        alarm_exprs.append(f"Machine_Alarm.StationAlarm[{idx}].Alarm")

    if alarm_exprs:
        lines.append("// 所有工站报警汇总")
        lines.append("Machine_Auto.bAnyStationAlarm :=")

        for i, expr in enumerate(alarm_exprs):
            end = ";" if i == len(alarm_exprs) - 1 else " OR"
            lines.append(f"    {expr}{end}")
    else:
        lines.append("Machine_Auto.bAnyStationAlarm := FALSE;")

    lines.append("")
    lines.append("Machine_Auto.bCanRun := Machine_Auto.bReady")
    lines.append("                       AND NOT Machine_Auto.bAnyStationAlarm;")
    lines.append("")

    lines.append("// ================================================================")
    lines.append("// 2. 统一复位逻辑")
    lines.append("// ================================================================")
    lines.append("IF Machine_Data.IN.bReset THEN")
    lines.append("    Machine_Auto.bComplete := FALSE;")
    lines.append("    Machine_Auto.bAnyStationAlarm := FALSE;")
    lines.append("    Machine_Auto.bCanRun := FALSE;")
    lines.append("")

    for i, st in enumerate(stations, start=1):
        sid = st["station_id"]
        sname = st["station_name"]
        idx = natural_station_index(sid, i)

        lines.append(f"    // Reset {sid} - {sname}")
        lines.append(f"    Station[{idx}].nAutoStep := 0;")
        lines.append(f"    Station[{idx}].bEnable := FALSE;")
        lines.append(f"    Station[{idx}].bRunning := FALSE;")
        lines.append(f"    Station[{idx}].bDone := FALSE;")
        lines.append(f"    Station[{idx}].bEstop := FALSE;")
        lines.append(f"    Machine_Alarm.StationAlarm[{idx}].Alarm := FALSE;")
        lines.append(f"    Machine_Alarm.StationAlarm[{idx}].AlarmNo := 0;")
        lines.append("")

    lines.append("END_IF;")
    lines.append("")

    lines.append("// ================================================================")
    lines.append("// 3. 多工站顺序互锁")
    lines.append("// ================================================================")

    previous_idx = None

    for i, st in enumerate(stations, start=1):
        sid = st["station_id"]
        sname = st["station_name"]
        idx = natural_station_index(sid, i)

        lines.append(f"// {sid} - {sname}")

        if previous_idx is None:
            lines.append(f"Station[{idx}].bEnable := Machine_Auto.bCanRun;")
        else:
            lines.append(f"Station[{idx}].bEnable := Machine_Auto.bCanRun")
            lines.append(f"                       AND Station[{previous_idx}].bDone;")

        lines.append(f"Station[{idx}].bEstop := NOT Station[{idx}].bEnable;")
        lines.append("")

        previous_idx = idx

    lines.append("// ================================================================")
    lines.append("// 4. 整机完成判断")
    lines.append("// ================================================================")

    if stations:
        last = stations[-1]
        last_idx = natural_station_index(last["station_id"], len(stations))
        lines.append(f"Machine_Auto.bComplete := Station[{last_idx}].bDone;")
    else:
        lines.append("Machine_Auto.bComplete := FALSE;")

    lines.append("")
    lines.append("// ================================================================")
    lines.append("// 5. HMI 推荐显示状态")
    lines.append("// ================================================================")
    lines.append("// Machine_Auto.bReady           : 整机就绪")
    lines.append("// Machine_Auto.bCanRun          : 整机允许运行")
    lines.append("// Machine_Auto.bAnyStationAlarm : 任意工站报警")
    lines.append("// Machine_Auto.bComplete        : 整机完成")
    lines.append("")

    return "\n".join(lines)