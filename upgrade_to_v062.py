from pathlib import Path
import zipfile
import json
import re
import csv
import io
from datetime import datetime

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")


def read_text_from_zip(z, name):
    raw = z.read(name)
    for enc in ["utf-8", "utf-8-sig", "gbk"]:
        try:
            return raw.decode(enc)
        except Exception:
            pass
    return raw.decode("utf-8", errors="ignore")


def find_latest_project_zip():
    zips = []

    for p in PROJECT_DIR.rglob("*.zip"):
        p_str = str(p).lower()
        p_name = p.name.lower()

        if ".venv" in p_str:
            continue

        if "source_backup" in p_name:
            continue

        if "backup" in p_name:
            continue

        if "v0.6.2" in p_name:
            continue

        zips.append(p)

    if not zips:
        return None

    return max(zips, key=lambda x: x.stat().st_mtime)


def detect_root_prefix(names):
    targets = [
        "00_README.txt",
        "manifest.json",
        "validation_report.txt",
    ]

    for target in targets:
        for name in names:
            n = name.replace("\\", "/")
            if n.endswith(target):
                return n[:-len(target)]

    return ""


def natural_station_index(station_id, fallback):
    text = str(station_id)
    nums = re.findall(r"\d+", text)
    if nums:
        return int(nums[-1])
    return fallback


def station_sort_key(cfg):
    sid = cfg.get("station_id") or cfg.get("id") or cfg.get("name") or ""
    nums = re.findall(r"\d+", str(sid))
    if nums:
        return int(nums[-1])
    return 999


def normalize_station_configs(stations):
    result = []
    seen = set()

    for i, cfg in enumerate(stations, start=1):
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

        if sid in seen:
            continue

        seen.add(sid)

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

    result.sort(key=station_sort_key)
    return result


def extract_station_configs(z, names):
    stations = []

    json_files = [
        n for n in names
        if "/configs/" in "/" + n.replace("\\", "/") and n.lower().endswith(".json")
    ]

    for jf in json_files:
        try:
            text = read_text_from_zip(z, jf)
            data = json.loads(text)
        except Exception:
            continue

        if isinstance(data, dict):
            if isinstance(data.get("station_configs"), list):
                stations.extend(data["station_configs"])

            elif isinstance(data.get("stations"), list):
                stations.extend(data["stations"])

            elif "station_id" in data or "station_name" in data:
                stations.append(data)

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and ("station_id" in item or "station_name" in item):
                    stations.append(item)

    stations = normalize_station_configs(stations)

    if stations:
        return stations

    # 如果 configs 里没提取到，就从 ST 文件名兜底识别
    fallback = []
    for n in names:
        text = n.replace("\\", "/")
        m = re.search(r"Station_(S\d+)", text, re.IGNORECASE)
        if m:
            sid = m.group(1).upper()
            fallback.append({
                "station_id": sid,
                "station_name": f"{sid}工站",
                "raw": {},
            })

    return normalize_station_configs(fallback)


def generate_machine_main_st(stations):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []

    lines.append("(*")
    lines.append("================================================================================")
    lines.append(" File    : 04_Machine_Auto_Main_Generated.st")
    lines.append(" Version : V0.6.2")
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
        sid = st["station_id"]
        idx = natural_station_index(sid, i)
        alarm_exprs.append(f"Machine_Alarm.StationAlarm[{idx}].Alarm")

    if alarm_exprs:
        lines.append("// 所有工站报警汇总")
        lines.append("Machine_Auto.bAnyStationAlarm := ")
        for i, expr in enumerate(alarm_exprs):
            end = ";" if i == len(alarm_exprs) - 1 else " OR"
            prefix = "    " if i > 0 else "    "
            lines.append(f"{prefix}{expr}{end}")
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


def generate_hmi_csv_bytes(stations):
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

    rows = [
        ["Machine", "Machine_Data.IN.bEstop", "急停输入", "BOOL", "Read", "整机急停状态"],
        ["Machine", "Machine_Data.IN.bSafety", "安全门/安全回路", "BOOL", "Read", "安全条件"],
        ["Machine", "Machine_Data.IN.bAirOn", "气源正常", "BOOL", "Read", "气压/气源状态"],
        ["Machine", "Machine_Data.IN.bReset", "复位按钮", "BOOL", "Read", "整机复位输入"],
        ["Machine", "Machine_Auto.bReady", "整机就绪", "BOOL", "Read", "安全、气源、急停均满足"],
        ["Machine", "Machine_Auto.bCanRun", "整机允许运行", "BOOL", "Read", "整机就绪且无工站报警"],
        ["Machine", "Machine_Auto.bAnyStationAlarm", "任意工站报警", "BOOL", "Read", "所有工站报警汇总"],
        ["Machine", "Machine_Auto.bComplete", "整机完成", "BOOL", "Read", "最后一个工站完成"],
    ]

    for r in rows:
        writer.writerow(r)

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

        for r in station_rows:
            writer.writerow(r)

    return output.getvalue().encode("utf-8-sig")


def update_manifest(old_text, stations):
    try:
        data = json.loads(old_text) if old_text else {}
        if not isinstance(data, dict):
            data = {"previous_manifest": data}
    except Exception:
        data = {"previous_manifest_raw": old_text}

    data["version"] = "V0.6.2"
    data["v062_generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["v062_features"] = [
        "整机主流程 ST 生成",
        "多工站顺序互锁",
        "工站报警汇总",
        "整机统一复位",
        "整机完成判断",
        "HMI 变量清单 CSV 生成",
    ]
    data["v062_added_files"] = [
        "04_Machine_Auto_Main_Generated.st",
        "HMI_Variable_List.csv",
    ]
    data["v062_station_chain"] = [
        {
            "station_id": st["station_id"],
            "station_name": st["station_name"],
        }
        for st in stations
    ]

    return json.dumps(data, ensure_ascii=False, indent=2)


def update_validation_report(old_text, stations):
    lines = []
    if old_text:
        lines.append(old_text.rstrip())
        lines.append("")

    lines.append("========== V0.6.2 增强验收 ==========")
    lines.append("✅ 已生成 04_Machine_Auto_Main_Generated.st")
    lines.append("✅ 已生成 HMI_Variable_List.csv")
    lines.append("✅ 已写入多工站顺序互锁逻辑")
    lines.append("✅ 已写入工站报警汇总逻辑")
    lines.append("✅ 已写入整机统一复位逻辑")
    lines.append("✅ 已写入整机完成判断逻辑")

    if stations:
        chain = " -> ".join([st["station_id"] for st in stations])
        lines.append(f"✅ 工站链路：{chain}")
    else:
        lines.append("⚠️ 未识别到工站链路")

    lines.append("")
    lines.append("V0.6.2 说明：")
    lines.append("本版本新增整机主流程层，负责多工站之间的顺序互锁、报警汇总、统一复位和整机完成状态。")
    lines.append("")

    return "\n".join(lines)


def find_entry_endswith(names, suffix):
    for n in names:
        if n.replace("\\", "/").endswith(suffix):
            return n
    return None


def main():
    source_zip = find_latest_project_zip()

    if not source_zip:
        print("❌ 没找到可升级的 V0.6.1 工程包 ZIP")
        return

    print("找到源工程包：")
    print(source_zip)

    out_zip = source_zip.with_name(source_zip.stem + "_V0.6.2.zip")

    with zipfile.ZipFile(source_zip, "r") as zin:
        names = zin.namelist()
        root_prefix = detect_root_prefix(names)

        stations = extract_station_configs(zin, names)

        if not stations:
            print("❌ 未识别到任何工站，无法生成 V0.6.2")
            return

        print("\n识别到工站：")
        for st in stations:
            print(f"  {st['station_id']} - {st['station_name']}")

        machine_st = generate_machine_main_st(stations)
        hmi_csv = generate_hmi_csv_bytes(stations)

        manifest_entry = find_entry_endswith(names, "manifest.json")
        validation_entry = find_entry_endswith(names, "validation_report.txt")

        old_manifest = read_text_from_zip(zin, manifest_entry) if manifest_entry else ""
        old_validation = read_text_from_zip(zin, validation_entry) if validation_entry else ""

        new_manifest = update_manifest(old_manifest, stations)
        new_validation = update_validation_report(old_validation, stations)

        station_chain_json = json.dumps({
            "version": "V0.6.2",
            "station_chain": [
                {
                    "station_id": st["station_id"],
                    "station_name": st["station_name"],
                    "station_index": natural_station_index(st["station_id"], i),
                }
                for i, st in enumerate(stations, start=1)
            ]
        }, ensure_ascii=False, indent=2)

        with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                n = info.filename.replace("\\", "/")

                skip_suffixes = [
                    "manifest.json",
                    "validation_report.txt",
                    "04_Machine_Auto_Main_Generated.st",
                    "HMI_Variable_List.csv",
                    "configs/v062_station_chain.json",
                ]

                if any(n.endswith(s) for s in skip_suffixes):
                    continue

                zout.writestr(info, zin.read(info.filename))

            zout.writestr(root_prefix + "04_Machine_Auto_Main_Generated.st", machine_st)
            zout.writestr(root_prefix + "HMI_Variable_List.csv", hmi_csv)
            zout.writestr(root_prefix + "configs/v062_station_chain.json", station_chain_json)
            zout.writestr(root_prefix + "manifest.json", new_manifest)
            zout.writestr(root_prefix + "validation_report.txt", new_validation)

    print("\n✅ V0.6.2 工程包已生成：")
    print(out_zip)


if __name__ == "__main__":
    main()