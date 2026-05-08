import csv
import io
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


def generate_hmi_variable_csv_text(station_configs):
    stations = normalize_station_configs(station_configs)

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

    base_rows = [
        ["Machine", "Machine_Data.IN.bEstop", "急停输入", "BOOL", "Read", "整机急停状态"],
        ["Machine", "Machine_Data.IN.bSafety", "安全门/安全回路", "BOOL", "Read", "安全条件"],
        ["Machine", "Machine_Data.IN.bAirOn", "气源正常", "BOOL", "Read", "气压/气源状态"],
        ["Machine", "Machine_Data.IN.bReset", "复位按钮", "BOOL", "Read", "整机复位输入"],
        ["Machine", "Machine_Auto.bReady", "整机就绪", "BOOL", "Read", "安全、气源、急停均满足"],
        ["Machine", "Machine_Auto.bCanRun", "整机允许运行", "BOOL", "Read", "整机就绪且无工站报警"],
        ["Machine", "Machine_Auto.bAnyStationAlarm", "任意工站报警", "BOOL", "Read", "所有工站报警汇总"],
        ["Machine", "Machine_Auto.bComplete", "整机完成", "BOOL", "Read", "最后一个工站完成"],
    ]

    for row in base_rows:
        writer.writerow(row)

    for i, st in enumerate(stations, start=1):
        sid = st["station_id"]
        sname = st["station_name"]
        idx = natural_station_index(sid, i)

        station_rows = [
            [sid, f"Station[{idx}].nAutoStep", f"{sname} 当前步号", "INT", "Read", "工站自动流程步号"],
            [sid, f"Station[{idx}].bEnable", f"{sname} 运行许可", "BOOL", "Read", "由整机主流程生成的工站使能"],
            [sid, f"Station[{idx}].bRunning", f"{sname} 运行中", "BOOL", "Read", "工站运行状态"],
            [sid, f"Station[{idx}].bDone", f"{sname} 完成", "BOOL", "Read", "工站流程完成"],
            [sid, f"Station[{idx}].bEstop", f"{sname} 停止/禁止", "BOOL", "Read", "工站被整机互锁禁止"],
            [sid, f"Machine_Alarm.StationAlarm[{idx}].Alarm", f"{sname} 报警", "BOOL", "Read", "工站报警状态"],
            [sid, f"Machine_Alarm.StationAlarm[{idx}].AlarmNo", f"{sname} 报警号", "INT", "Read", "工站报警编号"],
        ]

        for row in station_rows:
            writer.writerow(row)

    return output.getvalue()


def generate_hmi_variable_csv_bytes(station_configs):
    text = generate_hmi_variable_csv_text(station_configs)
    return text.encode("utf-8-sig")