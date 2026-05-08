import csv
import io
import re
from datetime import datetime


def natural_station_index(station_id, fallback):
    text = str(station_id)
    nums = re.findall(r"\d+", text)
    if nums:
        return int(nums[-1])
    return fallback


def normalize_station_configs(station_configs):
    result = []

    for i, cfg in enumerate(station_configs or [], start=1):
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


def normalize_cylinders(cylinder_config):
    cylinders = []

    for i, c in enumerate((cylinder_config or {}).get("cylinders", []), start=1):
        if not isinstance(c, dict):
            continue

        cyl_id = c.get("cylinder_id") or c.get("id") or c.get("name") or f"CY{i}"
        cyl_name = c.get("cylinder_name") or c.get("name") or f"{cyl_id}气缸"

        cylinders.append({
            "index": i,
            "cylinder_id": str(cyl_id),
            "cylinder_name": str(cyl_name),
            "raw": c,
        })

    return cylinders


def generate_dut_struct_st(cylinder_config, station_configs):
    stations = normalize_station_configs(station_configs)
    cylinders = normalize_cylinders(cylinder_config)
    station_count = max(len(stations), 1)
    cylinder_count = max(len(cylinders), 1)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("(*")
    lines.append("================================================================================")
    lines.append(" File    : 00_DUT_Struct_Generated.st")
    lines.append(" Version : V0.6.3")
    lines.append(" Author  : PLC Digital Engineer AI")
    lines.append(f" Time    : {now}")
    lines.append("")
    lines.append(" Purpose : Sysmac Studio 导入前 DUT / STRUCT 类型声明")
    lines.append("================================================================================")
    lines.append("*)")
    lines.append("")
    lines.append("TYPE")
    lines.append("")
    lines.append("    ST_CylinderIO : STRUCT")
    lines.append("        bOriginSensor : BOOL;")
    lines.append("        bWorkSensor   : BOOL;")
    lines.append("        bOriginValve  : BOOL;")
    lines.append("        bWorkValve    : BOOL;")
    lines.append("    END_STRUCT;")
    lines.append("")
    lines.append("    ST_CylinderCtrl : STRUCT")
    lines.append("        bCmdToOrigin  : BOOL;")
    lines.append("        bCmdToWork    : BOOL;")
    lines.append("        bBusy         : BOOL;")
    lines.append("        bDone         : BOOL;")
    lines.append("        bAlarm        : BOOL;")
    lines.append("        nAlarmNo      : INT;")
    lines.append("    END_STRUCT;")
    lines.append("")
    lines.append("    ST_StationAuto : STRUCT")
    lines.append("        nAutoStep : INT;")
    lines.append("        bEnable   : BOOL;")
    lines.append("        bRunning  : BOOL;")
    lines.append("        bDone     : BOOL;")
    lines.append("        bEstop    : BOOL;")
    lines.append("    END_STRUCT;")
    lines.append("")
    lines.append("    ST_MachineAuto : STRUCT")
    lines.append("        bReady           : BOOL;")
    lines.append("        bCanRun          : BOOL;")
    lines.append("        bAnyStationAlarm : BOOL;")
    lines.append("        bComplete        : BOOL;")
    lines.append("    END_STRUCT;")
    lines.append("")
    lines.append("    ST_StationAlarm : STRUCT")
    lines.append("        Alarm   : BOOL;")
    lines.append("        AlarmNo : INT;")
    lines.append("    END_STRUCT;")
    lines.append("")
    lines.append("    ST_MachineAlarm : STRUCT")
    lines.append(f"        StationAlarm : ARRAY[1..{station_count}] OF ST_StationAlarm;")
    lines.append("    END_STRUCT;")
    lines.append("")
    lines.append("    ST_MachineDataIN : STRUCT")
    lines.append("        bEstop  : BOOL;")
    lines.append("        bSafety : BOOL;")
    lines.append("        bAirOn  : BOOL;")
    lines.append("        bReset  : BOOL;")
    lines.append("    END_STRUCT;")
    lines.append("")
    lines.append("    ST_MachineData : STRUCT")
    lines.append("        IN : ST_MachineDataIN;")
    lines.append("    END_STRUCT;")
    lines.append("")
    lines.append("END_TYPE")
    lines.append("")
    lines.append("(*")
    lines.append("推荐数组规模：")
    lines.append(f"- Station       : ARRAY[1..{station_count}] OF ST_StationAuto")
    lines.append(f"- CylinderIO    : ARRAY[1..{cylinder_count}] OF ST_CylinderIO")
    lines.append(f"- CylinderCtrl  : ARRAY[1..{cylinder_count}] OF ST_CylinderCtrl")
    lines.append("*)")
    lines.append("")

    return "\n".join(lines)


def generate_global_variables_st(cylinder_config, station_configs):
    stations = normalize_station_configs(station_configs)
    cylinders = normalize_cylinders(cylinder_config)
    station_count = max(len(stations), 1)
    cylinder_count = max(len(cylinders), 1)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("(*")
    lines.append("================================================================================")
    lines.append(" File    : 00_Global_Variables_Generated.st")
    lines.append(" Version : V0.6.3")
    lines.append(" Author  : PLC Digital Engineer AI")
    lines.append(f" Time    : {now}")
    lines.append("")
    lines.append(" Purpose : Sysmac Studio 全局变量声明建议")
    lines.append("================================================================================")
    lines.append("*)")
    lines.append("")
    lines.append("VAR_GLOBAL")
    lines.append("    // 整机状态")
    lines.append("    Machine_Auto  : ST_MachineAuto;")
    lines.append("    Machine_Data  : ST_MachineData;")
    lines.append("    Machine_Alarm : ST_MachineAlarm;")
    lines.append("")
    lines.append("    // 工站状态")
    lines.append(f"    Station : ARRAY[1..{station_count}] OF ST_StationAuto;")
    lines.append("")
    lines.append("    // 气缸 IO / 控制")
    lines.append(f"    CylinderIO   : ARRAY[1..{cylinder_count}] OF ST_CylinderIO;")
    lines.append(f"    CylinderCtrl : ARRAY[1..{cylinder_count}] OF ST_CylinderCtrl;")
    lines.append("END_VAR")
    lines.append("")
    lines.append("(*")
    lines.append("工站索引：")
    for i, st in enumerate(stations, start=1):
        idx = natural_station_index(st["station_id"], i)
        lines.append(f"- Station[{idx}] = {st['station_id']} / {st['station_name']}")
    lines.append("")
    lines.append("气缸索引：")
    for c in cylinders:
        lines.append(f"- CylinderIO[{c['index']}] / CylinderCtrl[{c['index']}] = {c['cylinder_id']} / {c['cylinder_name']}")
    lines.append("*)")
    lines.append("")

    return "\n".join(lines)


def generate_io_mapping_csv_bytes(cylinder_config, station_configs):
    cylinders = normalize_cylinders(cylinder_config)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "category",
        "device_id",
        "device_name",
        "signal_name",
        "variable",
        "io_address",
        "data_type",
        "description",
    ])

    base_rows = [
        ["Machine", "MACHINE", "整机", "急停", "Machine_Data.IN.bEstop", "", "BOOL", "急停输入，需人工绑定实际IO"],
        ["Machine", "MACHINE", "整机", "安全回路", "Machine_Data.IN.bSafety", "", "BOOL", "安全门/安全继电器状态，需人工绑定实际IO"],
        ["Machine", "MACHINE", "整机", "气源正常", "Machine_Data.IN.bAirOn", "", "BOOL", "气压开关，需人工绑定实际IO"],
        ["Machine", "MACHINE", "整机", "复位按钮", "Machine_Data.IN.bReset", "", "BOOL", "复位按钮，需人工绑定实际IO"],
    ]

    for row in base_rows:
        writer.writerow(row)

    for c in cylinders:
        idx = c["index"]
        raw = c["raw"]

        mappings = [
            ["Cylinder", c["cylinder_id"], c["cylinder_name"], "原点传感器", f"CylinderIO[{idx}].bOriginSensor", raw.get("origin_sensor", ""), "BOOL", "气缸原点到位输入"],
            ["Cylinder", c["cylinder_id"], c["cylinder_name"], "动点传感器", f"CylinderIO[{idx}].bWorkSensor", raw.get("work_sensor", ""), "BOOL", "气缸动点到位输入"],
            ["Cylinder", c["cylinder_id"], c["cylinder_name"], "原点电磁阀", f"CylinderIO[{idx}].bOriginValve", raw.get("origin_valve", ""), "BOOL", "气缸回原点输出"],
            ["Cylinder", c["cylinder_id"], c["cylinder_name"], "动点电磁阀", f"CylinderIO[{idx}].bWorkValve", raw.get("work_valve", ""), "BOOL", "气缸到动点输出"],
        ]

        for row in mappings:
            writer.writerow(row)

    return output.getvalue().encode("utf-8-sig")


def generate_sysmac_import_guide_txt(cylinder_config, station_configs):
    stations = normalize_station_configs(station_configs)
    cylinders = normalize_cylinders(cylinder_config)

    lines = []
    lines.append("Sysmac Studio 导入说明 - V0.6.3")
    lines.append("=" * 80)
    lines.append("")
    lines.append("一、推荐导入顺序")
    lines.append("1. 先导入或手动创建 DUT：00_DUT_Struct_Generated.st")
    lines.append("2. 再导入或手动创建全局变量：00_Global_Variables_Generated.st")
    lines.append("3. 导入模板功能块：template_source 目录下的 FB / ST 文件")
    lines.append("4. 导入气缸动作程序：01_Cylinder_Action_Generated.st")
    lines.append("5. 导入各工站程序：02_Station_*.st、03_Station_*.st ...")
    lines.append("6. 最后导入整机主流程：04_Machine_Auto_Main_Generated.st")
    lines.append("")
    lines.append("二、需要人工确认的内容")
    lines.append("- IO_Mapping_List.csv 中的实际 IO 地址是否正确")
    lines.append("- Station 数组长度是否满足实际工站数量")
    lines.append("- CylinderIO / CylinderCtrl 数组长度是否满足实际气缸数量")
    lines.append("- 报警号是否符合客户标准")
    lines.append("- 自动流程步号是否符合公司编程规范")
    lines.append("")
    lines.append("三、当前工站链路")
    if stations:
        chain = " -> ".join([f"{s['station_id']}({s['station_name']})" for s in stations])
        lines.append(chain)
    else:
        lines.append("未识别到工站。")
    lines.append("")
    lines.append("四、当前气缸清单")
    if cylinders:
        for c in cylinders:
            lines.append(f"- {c['index']}: {c['cylinder_id']} / {c['cylinder_name']}")
    else:
        lines.append("未识别到气缸。")
    lines.append("")
    lines.append("五、重要说明")
    lines.append("本工具生成的是 Sysmac Studio 导入前的工程文本包。")
    lines.append("正式上机前必须由 PLC 工程师完成 IO 绑定、仿真验证、单步调试和安全确认。")
    lines.append("")

    return "\n".join(lines)
