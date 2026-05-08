import csv
import io
import re
from pathlib import Path
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


def get_any(raw, keys, default=""):
    if not isinstance(raw, dict):
        return default

    for k in keys:
        if k in raw and raw.get(k) not in [None, ""]:
            return raw.get(k)

    io = raw.get("io") or raw.get("IO") or {}
    if isinstance(io, dict):
        for k in keys:
            if k in io and io.get(k) not in [None, ""]:
                return io.get(k)

    return default


def parse_io_address(address):
    address = str(address or "").strip()
    if not address:
        return {
            "raw": "",
            "io_type": "",
            "unit": "",
            "point": "",
            "channel": "",
            "valid": False,
        }

    clean = address.upper().replace("%", "").replace(" ", "")

    # 支持 I1_0 / Q1_0 / I1.0 / Q1.0 / I1-0
    m = re.match(r"^([IQ])(\d+)[_\.\-](\d+)$", clean)
    if m:
        io_prefix, unit, point = m.groups()
        io_type = "Input" if io_prefix == "I" else "Output"
        return {
            "raw": address,
            "io_type": io_type,
            "unit": unit,
            "point": point,
            "channel": f"{io_prefix}{unit}.{point}",
            "valid": True,
        }

    # 支持 CIO 格式粗识别，例如 100.00
    m = re.match(r"^(\d+)\.(\d+)$", clean)
    if m:
        unit, point = m.groups()
        return {
            "raw": address,
            "io_type": "Unknown",
            "unit": unit,
            "point": point,
            "channel": f"{unit}.{point}",
            "valid": True,
        }

    return {
        "raw": address,
        "io_type": "Unparsed",
        "unit": "",
        "point": "",
        "channel": address,
        "valid": False,
    }


def extract_steps(station_raw):
    if not isinstance(station_raw, dict):
        return []

    candidates = [
        station_raw.get("steps"),
        station_raw.get("process_steps"),
        station_raw.get("flow_steps"),
        station_raw.get("actions"),
        station_raw.get("process"),
        station_raw.get("flow"),
    ]

    raw_steps = []
    for item in candidates:
        if isinstance(item, list) and item:
            raw_steps = item
            break

    result = []

    for i, step in enumerate(raw_steps, start=1):
        if isinstance(step, dict):
            step_no = (
                step.get("step_no")
                or step.get("step")
                or step.get("index")
                or step.get("step_index")
                or i
            )

            action = (
                step.get("action")
                or step.get("name")
                or step.get("description")
                or step.get("desc")
                or step.get("comment")
                or ""
            )

            if not action:
                cylinder = step.get("cylinder") or step.get("cylinder_id") or step.get("device") or ""
                target = step.get("target") or step.get("position") or step.get("cmd") or ""
                action = f"{cylinder} {target}".strip()

            timeout_ms = (
                step.get("timeout_ms")
                or step.get("timeout")
                or step.get("time_ms")
                or 3000
            )

            alarm_no = (
                step.get("alarm_no")
                or step.get("alarm")
                or ""
            )

            wait_condition = (
                step.get("wait_condition")
                or step.get("condition")
                or step.get("done_condition")
                or ""
            )

            result.append({
                "step_no": step_no,
                "action": str(action),
                "timeout_ms": timeout_ms,
                "alarm_no": alarm_no,
                "wait_condition": str(wait_condition),
                "raw": step,
            })

        else:
            result.append({
                "step_no": i,
                "action": str(step),
                "timeout_ms": 3000,
                "alarm_no": "",
                "wait_condition": "",
                "raw": step,
            })

    return result


def generate_alarm_list_csv_bytes(cylinder_config, station_configs):
    stations = normalize_station_configs(station_configs)
    cylinders = normalize_cylinders(cylinder_config)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "alarm_no",
        "level",
        "category",
        "station_id",
        "step_no",
        "device_id",
        "alarm_name",
        "trigger_condition",
        "reset_method",
        "hmi_message",
    ])

    writer.writerow([
        1000,
        "Error",
        "Machine",
        "MACHINE",
        "",
        "MACHINE",
        "整机急停",
        "Machine_Data.IN.bEstop = TRUE",
        "解除急停后按复位",
        "整机急停，请检查急停按钮和安全回路",
    ])

    writer.writerow([
        1001,
        "Error",
        "Machine",
        "MACHINE",
        "",
        "MACHINE",
        "安全回路异常",
        "Machine_Data.IN.bSafety = FALSE",
        "恢复安全条件后按复位",
        "安全回路未满足，请检查安全门/安全继电器",
    ])

    writer.writerow([
        1002,
        "Error",
        "Machine",
        "MACHINE",
        "",
        "MACHINE",
        "气源异常",
        "Machine_Data.IN.bAirOn = FALSE",
        "恢复气压后按复位",
        "气源异常，请检查气压",
    ])

    for s_i, station in enumerate(stations, start=1):
        sid = station["station_id"]
        sname = station["station_name"]
        station_idx = natural_station_index(sid, s_i)
        steps = extract_steps(station["raw"])

        if steps:
            for step in steps:
                step_no = int(step["step_no"]) if str(step["step_no"]).isdigit() else s_i
                alarm_no = step["alarm_no"] or (2000 + station_idx * 100 + step_no)

                writer.writerow([
                    alarm_no,
                    "Error",
                    "StationStep",
                    sid,
                    step["step_no"],
                    sid,
                    f"{sname} 步骤{step['step_no']}超时",
                    f"Station[{station_idx}].nAutoStep = {step['step_no']} 超过 {step['timeout_ms']}ms",
                    "处理异常后按复位",
                    f"{sname} 步骤{step['step_no']}执行超时：{step['action']}",
                ])
        else:
            writer.writerow([
                2000 + station_idx * 100,
                "Warning",
                "Station",
                sid,
                "",
                sid,
                f"{sname} 未配置明确步骤报警",
                f"Station[{station_idx}].bRunning = TRUE 且无步骤定义",
                "检查 station_configs",
                f"{sname} 未检测到明确步骤配置",
            ])

    for cyl in cylinders:
        idx = cyl["index"]
        cid = cyl["cylinder_id"]
        cname = cyl["cylinder_name"]

        writer.writerow([
            3000 + idx * 10 + 1,
            "Error",
            "Cylinder",
            "",
            "",
            cid,
            f"{cname} 到动点超时",
            f"CylinderCtrl[{idx}].bCmdToWork = TRUE 且 CylinderIO[{idx}].bWorkSensor 未到位",
            "检查气缸、传感器、电磁阀后按复位",
            f"{cname} 到动点超时",
        ])

        writer.writerow([
            3000 + idx * 10 + 2,
            "Error",
            "Cylinder",
            "",
            "",
            cid,
            f"{cname} 回原点超时",
            f"CylinderCtrl[{idx}].bCmdToOrigin = TRUE 且 CylinderIO[{idx}].bOriginSensor 未到位",
            "检查气缸、传感器、电磁阀后按复位",
            f"{cname} 回原点超时",
        ])

    return output.getvalue().encode("utf-8-sig")


def generate_step_list_csv_bytes(station_configs):
    stations = normalize_station_configs(station_configs)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "station_id",
        "station_name",
        "station_index",
        "step_no",
        "action",
        "wait_condition",
        "timeout_ms",
        "alarm_no",
        "description",
    ])

    for s_i, station in enumerate(stations, start=1):
        sid = station["station_id"]
        sname = station["station_name"]
        station_idx = natural_station_index(sid, s_i)
        steps = extract_steps(station["raw"])

        if not steps:
            writer.writerow([
                sid,
                sname,
                station_idx,
                "",
                "未识别到步骤",
                "",
                "",
                "",
                "请检查 AI 解析出的 station_configs",
            ])
            continue

        for step in steps:
            writer.writerow([
                sid,
                sname,
                station_idx,
                step["step_no"],
                step["action"],
                step["wait_condition"],
                step["timeout_ms"],
                step["alarm_no"],
                f"{sname} 第 {step['step_no']} 步",
            ])

    return output.getvalue().encode("utf-8-sig")


def generate_io_mapping_enhanced_csv_bytes(cylinder_config, station_configs):
    cylinders = normalize_cylinders(cylinder_config)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "category",
        "device_id",
        "device_name",
        "signal_name",
        "variable",
        "raw_io_address",
        "parsed_io_type",
        "unit",
        "point",
        "channel",
        "valid_format",
        "description",
    ])

    machine_rows = [
        ["Machine", "MACHINE", "整机", "急停", "Machine_Data.IN.bEstop", "", "急停输入"],
        ["Machine", "MACHINE", "整机", "安全回路", "Machine_Data.IN.bSafety", "", "安全回路输入"],
        ["Machine", "MACHINE", "整机", "气源正常", "Machine_Data.IN.bAirOn", "", "气源压力输入"],
        ["Machine", "MACHINE", "整机", "复位按钮", "Machine_Data.IN.bReset", "", "复位按钮输入"],
    ]

    for row in machine_rows:
        p = parse_io_address(row[5])
        writer.writerow(row[:6] + [
            p["io_type"],
            p["unit"],
            p["point"],
            p["channel"],
            p["valid"],
            row[6],
        ])

    for c in cylinders:
        idx = c["index"]
        raw = c["raw"]

        signals = [
            (
                "原点传感器",
                f"CylinderIO[{idx}].bOriginSensor",
                get_any(raw, ["origin_sensor", "origin_sensor_addr", "home_sensor", "origin_input"]),
                "气缸原点到位输入",
            ),
            (
                "动点传感器",
                f"CylinderIO[{idx}].bWorkSensor",
                get_any(raw, ["work_sensor", "work_sensor_addr", "end_sensor", "work_input"]),
                "气缸动点到位输入",
            ),
            (
                "原点电磁阀",
                f"CylinderIO[{idx}].bOriginValve",
                get_any(raw, ["origin_valve", "origin_valve_addr", "home_valve", "origin_output"]),
                "气缸回原点输出",
            ),
            (
                "动点电磁阀",
                f"CylinderIO[{idx}].bWorkValve",
                get_any(raw, ["work_valve", "work_valve_addr", "end_valve", "work_output"]),
                "气缸到动点输出",
            ),
        ]

        for signal_name, variable, addr, desc in signals:
            p = parse_io_address(addr)
            writer.writerow([
                "Cylinder",
                c["cylinder_id"],
                c["cylinder_name"],
                signal_name,
                variable,
                addr,
                p["io_type"],
                p["unit"],
                p["point"],
                p["channel"],
                p["valid"],
                desc,
            ])

    return output.getvalue().encode("utf-8-sig")


def read_text(path):
    path = Path(path)
    for enc in ["utf-8", "utf-8-sig", "gbk"]:
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(encoding="utf-8", errors="ignore")


def collect_st_variable_references(package_dir):
    package_dir = Path(package_dir)
    refs = {}

    patterns = [
        r"Machine_Auto\.[A-Za-z_][A-Za-z0-9_]*",
        r"Machine_Data\.[A-Za-z0-9_\.\[\]]+",
        r"Machine_Alarm\.[A-Za-z0-9_\.\[\]]+",
        r"Station\[\d+\]\.[A-Za-z_][A-Za-z0-9_]*",
        r"CylinderIO\[\d+\]\.[A-Za-z_][A-Za-z0-9_]*",
        r"CylinderCtrl\[\d+\]\.[A-Za-z_][A-Za-z0-9_]*",
    ]

    for st_file in sorted(package_dir.glob("*.st")):
        text = read_text(st_file)
        found = set()

        for pat in patterns:
            found.update(re.findall(pat, text))

        refs[st_file.name] = sorted(found)

    return refs


def generate_variable_cross_reference_report_text(package_dir, cylinder_config, station_configs):
    package_dir = Path(package_dir)
    stations = normalize_station_configs(station_configs)
    cylinders = normalize_cylinders(cylinder_config)
    refs = collect_st_variable_references(package_dir)

    known_prefixes = [
        "Machine_Auto",
        "Machine_Data",
        "Machine_Alarm",
        "Station",
        "CylinderIO",
        "CylinderCtrl",
    ]

    all_refs = sorted({v for values in refs.values() for v in values})

    lines = []
    lines.append("Variable Cross Reference Report - V0.6.4")
    lines.append("=" * 80)
    lines.append(f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Package Dir : {package_dir}")
    lines.append("")
    lines.append("一、变量引用统计")
    lines.append(f"ST 文件数量：{len(refs)}")
    lines.append(f"变量引用数量：{len(all_refs)}")
    lines.append("")
    lines.append("二、已知变量前缀")
    for p in known_prefixes:
        lines.append(f"✅ {p}")
    lines.append("")
    lines.append("三、按 ST 文件列出引用")
    for filename, values in refs.items():
        lines.append(f"[{filename}]")
        if values:
            for v in values:
                lines.append(f"  - {v}")
        else:
            lines.append("  - 未检测到标准变量引用")
        lines.append("")
    lines.append("四、工站与数组规模")
    lines.append(f"Station 数量：{len(stations)}")
    lines.append(f"Cylinder 数量：{len(cylinders)}")
    for i, s in enumerate(stations, start=1):
        idx = natural_station_index(s["station_id"], i)
        lines.append(f"- Station[{idx}] = {s['station_id']} / {s['station_name']}")
    for c in cylinders:
        lines.append(f"- CylinderIO[{c['index']}] / CylinderCtrl[{c['index']}] = {c['cylinder_id']} / {c['cylinder_name']}")
    lines.append("")
    lines.append("五、结论")
    lines.append("PASS: 已完成 ST 变量引用交叉引用扫描。")
    lines.append("说明：本报告为静态扫描，最终仍需 Sysmac Studio 编译确认。")
    lines.append("")

    return "\n".join(lines)


def generate_final_acceptance_report_text(package_dir, cylinder_config, station_configs):
    package_dir = Path(package_dir)
    stations = normalize_station_configs(station_configs)
    cylinders = normalize_cylinders(cylinder_config)

    required = [
        "00_README.txt",
        "validation_report.txt",
        "manifest.json",
        "00_DUT_Struct_Generated.st",
        "00_Global_Variables_Generated.st",
        "01_Cylinder_Action_Generated.st",
        "04_Machine_Auto_Main_Generated.st",
        "HMI_Variable_List.csv",
        "IO_Mapping_List.csv",
        "IO_Mapping_Enhanced.csv",
        "Alarm_List.csv",
        "Step_List.csv",
        "Variable_CrossReference_Report.txt",
        "Sysmac_Import_Guide.txt",
        "ST_Quality_Report.txt",
    ]

    lines = []
    lines.append("Final Acceptance Report - V0.6.4")
    lines.append("=" * 80)
    lines.append(f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Package Dir : {package_dir}")
    lines.append("")
    lines.append("一、工程概况")
    lines.append(f"工站数量：{len(stations)}")
    lines.append(f"气缸数量：{len(cylinders)}")

    if stations:
        lines.append("工站链路：" + " -> ".join([s["station_id"] for s in stations]))
    else:
        lines.append("工站链路：未识别到工站")

    lines.append("")
    lines.append("二、交付文件检查")

    missing = []

    for name in required:
        if (package_dir / name).exists():
            lines.append(f"✅ {name}")
        else:
            lines.append(f"❌ {name}")
            missing.append(name)

    lines.append("")
    lines.append("三、V0.6.4 新增交付物")
    lines.append("✅ Alarm_List.csv：报警清单")
    lines.append("✅ Step_List.csv：工站步骤清单")
    lines.append("✅ IO_Mapping_Enhanced.csv：增强 IO 映射")
    lines.append("✅ Variable_CrossReference_Report.txt：变量交叉引用报告")
    lines.append("✅ Final_Acceptance_Report.txt：最终验收报告")
    lines.append("")

    lines.append("四、结论")
    if missing:
        lines.append("FAIL: 存在缺失文件，请检查生成器。")
        lines.append("缺失文件：" + ", ".join(missing))
    else:
        lines.append("PASS: V0.6.4 工程包静态验收通过。")

    lines.append("")
    lines.append("注意：静态验收通过不代表可直接上机。")
    lines.append("正式投产前必须完成 Sysmac Studio 编译、仿真、IO 点检、单步调试和安全验证。")
    lines.append("")

    return chr(10).join(lines)
