from pathlib import Path
from datetime import datetime
import shutil
import textwrap

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")
GEN_DIR = PROJECT_DIR / "company_generators"

MULTI_GEN = GEN_DIR / "multi_station_project_generator.py"
SYSMAC_GEN = GEN_DIR / "sysmac_export_generator.py"
QUALITY_GEN = GEN_DIR / "st_quality_checker.py"
CHECK_SCRIPT = PROJECT_DIR / "check_v063_product_core.py"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print("✅ 写入：", path)


def backup_file(path: Path):
    if not path.exists():
        return None
    backup = path.with_name(f"{path.stem}_backup_v063_{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}")
    shutil.copy2(path, backup)
    print("✅ 备份：", backup)
    return backup


def ensure_replace(text: str, old: str, new: str, label: str):
    if old not in text:
        print(f"⚠️ 未找到插入点：{label}")
        return text, False
    text = text.replace(old, new, 1)
    print(f"✅ 已处理：{label}")
    return text, True


def install_sysmac_export_generator():
    content = r'''
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
'''
    write_file(SYSMAC_GEN, content)


def install_st_quality_checker():
    content = r'''
from pathlib import Path
from datetime import datetime
import re


REQUIRED_ST_FILES = [
    "00_DUT_Struct_Generated.st",
    "00_Global_Variables_Generated.st",
    "01_Cylinder_Action_Generated.st",
    "04_Machine_Auto_Main_Generated.st",
]


def read_text(path: Path):
    for enc in ["utf-8", "utf-8-sig", "gbk"]:
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(encoding="utf-8", errors="ignore")


def generate_st_quality_report_text(package_dir, station_configs=None):
    package_dir = Path(package_dir)
    station_configs = station_configs or []

    lines = []
    lines.append("ST Quality Report - V0.6.3")
    lines.append("=" * 80)
    lines.append(f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Package Dir : {package_dir}")
    lines.append("")

    ok_count = 0
    warn_count = 0
    err_count = 0

    def ok(msg):
        nonlocal ok_count
        ok_count += 1
        lines.append("✅ " + msg)

    def warn(msg):
        nonlocal warn_count
        warn_count += 1
        lines.append("⚠️ " + msg)

    def err(msg):
        nonlocal err_count
        err_count += 1
        lines.append("❌ " + msg)

    lines.append("一、必要 ST 文件检查")
    for name in REQUIRED_ST_FILES:
        p = package_dir / name
        if p.exists():
            ok(f"存在：{name}")
        else:
            err(f"缺少：{name}")

    station_files = sorted(package_dir.glob("*_Station_*.st"))
    if station_files:
        ok(f"检测到工站 ST 文件数量：{len(station_files)}")
    else:
        err("未检测到工站 ST 文件")

    lines.append("")
    lines.append("二、整机主流程关键词检查")
    machine_file = package_dir / "04_Machine_Auto_Main_Generated.st"
    if machine_file.exists():
        text = read_text(machine_file)

        checks = [
            ("Machine_Auto.bReady", "整机就绪"),
            ("Machine_Auto.bCanRun", "整机允许运行"),
            ("Machine_Auto.bAnyStationAlarm", "报警汇总"),
            ("Machine_Data.IN.bReset", "统一复位"),
            ("Machine_Auto.bComplete", "整机完成"),
        ]

        for kw, desc in checks:
            if kw in text:
                ok(f"整机主流程包含：{desc} / {kw}")
            else:
                err(f"整机主流程缺少：{desc} / {kw}")

        if "Station[1].bDone" in text:
            ok("检测到后续工站等待前工站 Done 的互锁逻辑")
        else:
            warn("未明显检测到 Station[1].bDone 互锁关键词")
    else:
        err("无法检查整机主流程，文件不存在")

    lines.append("")
    lines.append("三、DUT / 全局变量检查")
    dut_file = package_dir / "00_DUT_Struct_Generated.st"
    global_file = package_dir / "00_Global_Variables_Generated.st"

    if dut_file.exists():
        dut = read_text(dut_file)
        for kw in ["ST_StationAuto", "ST_MachineAuto", "ST_MachineAlarm", "ST_MachineData", "ST_CylinderIO"]:
            if kw in dut:
                ok(f"DUT 包含：{kw}")
            else:
                err(f"DUT 缺少：{kw}")

    if global_file.exists():
        gv = read_text(global_file)
        for kw in ["VAR_GLOBAL", "Machine_Auto", "Machine_Data", "Machine_Alarm", "Station : ARRAY", "CylinderIO"]:
            if kw in gv:
                ok(f"全局变量包含：{kw}")
            else:
                err(f"全局变量缺少：{kw}")

    lines.append("")
    lines.append("四、工站程序步号粗检查")
    for st_file in station_files:
        text = read_text(st_file)
        steps = re.findall(r"(?:nAutoStep|AutoStep)\s*:=\s*(\d+)", text)
        if steps:
            ok(f"{st_file.name} 检测到步号赋值：{', '.join(steps[:12])}")
        else:
            warn(f"{st_file.name} 未检测到明显步号赋值")

        if "Alarm" in text or "报警" in text:
            ok(f"{st_file.name} 包含报警关键词")
        else:
            warn(f"{st_file.name} 未明显包含报警关键词")

    lines.append("")
    lines.append("五、结论")
    lines.append(f"OK: {ok_count}")
    lines.append(f"WARNING: {warn_count}")
    lines.append(f"ERROR: {err_count}")

    if err_count == 0:
        lines.append("✅ V0.6.3 ST 质量检查通过：未发现致命缺失。")
    else:
        lines.append("❌ V0.6.3 ST 质量检查未通过：存在必要文件或关键结构缺失。")

    lines.append("")
    lines.append("说明：本报告是静态检查报告，不能替代 Sysmac Studio 编译、仿真和现场调试。")
    lines.append("")

    return "\n".join(lines)
'''
    write_file(QUALITY_GEN, content)


def patch_multi_station_generator():
    if not MULTI_GEN.exists():
        print("❌ 找不到：", MULTI_GEN)
        return False

    backup_file(MULTI_GEN)
    text = MULTI_GEN.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")
    success = True

    if 'GENERATOR_VERSION = "V0.6.3"' not in text:
        if 'GENERATOR_VERSION = "V0.6.2.1"' in text:
            text = text.replace('GENERATOR_VERSION = "V0.6.2.1"', 'GENERATOR_VERSION = "V0.6.3"', 1)
            print("✅ 版本号 V0.6.2.1 → V0.6.3")
        elif 'GENERATOR_VERSION = "V0.6"' in text:
            text = text.replace('GENERATOR_VERSION = "V0.6"', 'GENERATOR_VERSION = "V0.6.3"', 1)
            print("✅ 版本号 V0.6 → V0.6.3")
        else:
            print("⚠️ 未找到 GENERATOR_VERSION 原始版本号")

    if "sysmac_export_generator" not in text:
        old = '''from company_generators.hmi_variable_generator import (
    generate_hmi_variable_csv_bytes
)
'''
        new = '''from company_generators.hmi_variable_generator import (
    generate_hmi_variable_csv_bytes
)

from company_generators.sysmac_export_generator import (
    generate_dut_struct_st,
    generate_global_variables_st,
    generate_io_mapping_csv_bytes,
    generate_sysmac_import_guide_txt
)

from company_generators.st_quality_checker import (
    generate_st_quality_report_text
)
'''
        text, ok = ensure_replace(text, old, new, "增加 V0.6.3 import")
        success = success and ok
    else:
        print("✅ V0.6.3 import 已存在")

    if "def write_bytes(" not in text:
        old = '''def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
'''
        new = '''def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_bytes(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
'''
        text, ok = ensure_replace(text, old, new, "增加 write_bytes")
        success = success and ok
    else:
        print("✅ write_bytes 已存在")

    if "V0.6.3 Sysmac Studio 导入前工程规范增强" not in text:
        old = '''    readme_path = package_dir / "00_README.txt"
    validation_path = package_dir / "validation_report.txt"
'''
        new = '''    validation_text += (
        "\\n\\n========== V0.6.3 Sysmac Studio 导入前工程规范增强 ==========\\n"
        "✅ 已生成 00_DUT_Struct_Generated.st\\n"
        "✅ 已生成 00_Global_Variables_Generated.st\\n"
        "✅ 已生成 IO_Mapping_List.csv\\n"
        "✅ 已生成 Sysmac_Import_Guide.txt\\n"
        "✅ 已生成 ST_Quality_Report.txt\\n"
        "✅ 已增强变量声明、DUT结构、IO映射和导入说明\\n"
    )

    readme_path = package_dir / "00_README.txt"
    validation_path = package_dir / "validation_report.txt"
'''
        text, ok = ensure_replace(text, old, new, "增强 validation_report V0.6.3")
        success = success and ok
    else:
        print("✅ validation_report V0.6.3 已存在")

    if 'dut_struct_path = package_dir / "00_DUT_Struct_Generated.st"' not in text:
        old = '''    # V0.6.2.1：HMI 变量清单
    hmi_variable_path = package_dir / "HMI_Variable_List.csv"
    write_bytes(hmi_variable_path, generate_hmi_variable_csv_bytes(station_configs))
    files_written.append((hmi_variable_path, "hmi_variable"))

    configs_dir = package_dir / "configs"
'''
        new = '''    # V0.6.2.1：HMI 变量清单
    hmi_variable_path = package_dir / "HMI_Variable_List.csv"
    write_bytes(hmi_variable_path, generate_hmi_variable_csv_bytes(station_configs))
    files_written.append((hmi_variable_path, "hmi_variable"))

    # V0.6.3：Sysmac Studio 导入前 DUT / 全局变量 / IO映射 / 导入说明
    dut_struct_path = package_dir / "00_DUT_Struct_Generated.st"
    write_text(dut_struct_path, generate_dut_struct_st(cylinder_config, station_configs))
    files_written.append((dut_struct_path, "generated_st"))

    global_variables_path = package_dir / "00_Global_Variables_Generated.st"
    write_text(global_variables_path, generate_global_variables_st(cylinder_config, station_configs))
    files_written.append((global_variables_path, "generated_st"))

    io_mapping_path = package_dir / "IO_Mapping_List.csv"
    write_bytes(io_mapping_path, generate_io_mapping_csv_bytes(cylinder_config, station_configs))
    files_written.append((io_mapping_path, "io_mapping"))

    sysmac_guide_path = package_dir / "Sysmac_Import_Guide.txt"
    write_text(sysmac_guide_path, generate_sysmac_import_guide_txt(cylinder_config, station_configs))
    files_written.append((sysmac_guide_path, "document"))

    configs_dir = package_dir / "configs"
'''
        text, ok = ensure_replace(text, old, new, "接入 V0.6.3 DUT / Global / IO / Guide")
        success = success and ok
    else:
        print("✅ V0.6.3 核心文件生成逻辑已存在")

    if 'st_quality_report_path = package_dir / "ST_Quality_Report.txt"' not in text:
        old = '''    file_records = [
        build_file_record(path, package_dir, category)
        for path, category in files_written
    ]
'''
        new = '''    # V0.6.3：ST 静态质量检查报告
    st_quality_report_path = package_dir / "ST_Quality_Report.txt"
    write_text(
        st_quality_report_path,
        generate_st_quality_report_text(package_dir, station_configs)
    )
    files_written.append((st_quality_report_path, "document"))

    file_records = [
        build_file_record(path, package_dir, category)
        for path, category in files_written
    ]
'''
        text, ok = ensure_replace(text, old, new, "接入 ST_Quality_Report.txt")
        success = success and ok
    else:
        print("✅ ST_Quality_Report.txt 生成逻辑已存在")

    if '"v063_features"' not in text:
        old = '''    manifest_path = package_dir / "manifest.json"
'''
        new = '''    # V0.6.3：manifest 增强信息
    manifest["version"] = GENERATOR_VERSION
    manifest["v063_generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    manifest["v063_features"] = [
        "Sysmac Studio 导入前 DUT 结构生成",
        "全局变量声明生成",
        "IO 映射清单生成",
        "Sysmac 导入说明生成",
        "ST 静态质量检查报告生成"
    ]
    manifest["v063_added_files"] = [
        "00_DUT_Struct_Generated.st",
        "00_Global_Variables_Generated.st",
        "IO_Mapping_List.csv",
        "Sysmac_Import_Guide.txt",
        "ST_Quality_Report.txt"
    ]

    manifest_path = package_dir / "manifest.json"
'''
        text, ok = ensure_replace(text, old, new, "增强 manifest V0.6.3")
        success = success and ok
    else:
        print("✅ manifest V0.6.3 已存在")

    if success:
        MULTI_GEN.write_text(text, encoding="utf-8")
        print("✅ multi_station_project_generator.py 已升级到 V0.6.3")
    else:
        print("❌ multi_station_project_generator.py 部分补丁未成功，请把输出发给我")

    return success


def install_check_script():
    content = r'''
from pathlib import Path
import zipfile
import json
import csv
import io

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")
ZIP_PATH = PROJECT_DIR / "output" / "AI_Device_Project_Package_V06.zip"


def read_text(z, name):
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
    print("========== V0.6.3 自动生成工程包 ==========")

    from company_generators.multi_station_project_generator import generate_multi_station_project_package_from_file

    result = generate_multi_station_project_package_from_file()
    print("生成结果：", result.get("ok"))
    print("ZIP：", result.get("zip_path"))

    if not result.get("ok"):
        print("❌ 工程包生成失败：")
        for e in result.get("errors", []):
            print(e)
        return

    if not ZIP_PATH.exists():
        print("❌ ZIP 不存在：", ZIP_PATH)
        return

    print("\n========== V0.6.3 ZIP 检查 ==========")
    print(ZIP_PATH)

    ok = True

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        names = z.namelist()

        required = [
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
            "Sysmac_Import_Guide.txt",
            "ST_Quality_Report.txt",
            "configs/cylinder_config.json",
            "configs/station_configs.json",
            "configs/v062_station_chain.json",
            "configs/company_symbols.json",
            "template_source/FB_Cylinder.st",
        ]

        print("\n========== 1. 必要文件检查 ==========")
        for f in required:
            if find_endswith(names, f):
                print(f"✅ {f}")
            else:
                print(f"❌ 缺少 {f}")
                ok = False

        print("\n========== 2. DUT 结构检查 ==========")
        dut_name = find_endswith(names, "00_DUT_Struct_Generated.st")
        if dut_name:
            dut = read_text(z, dut_name)
            for kw in ["TYPE", "ST_StationAuto", "ST_MachineAuto", "ST_MachineAlarm", "ST_MachineData", "ST_CylinderIO"]:
                if kw in dut:
                    print(f"✅ DUT 包含：{kw}")
                else:
                    print(f"❌ DUT 缺少：{kw}")
                    ok = False
        else:
            ok = False

        print("\n========== 3. 全局变量检查 ==========")
        gv_name = find_endswith(names, "00_Global_Variables_Generated.st")
        if gv_name:
            gv = read_text(z, gv_name)
            for kw in ["VAR_GLOBAL", "Machine_Auto", "Machine_Data", "Machine_Alarm", "Station : ARRAY", "CylinderIO", "CylinderCtrl"]:
                if kw in gv:
                    print(f"✅ 全局变量包含：{kw}")
                else:
                    print(f"❌ 全局变量缺少：{kw}")
                    ok = False
        else:
            ok = False

        print("\n========== 4. IO 映射 CSV 检查 ==========")
        io_name = find_endswith(names, "IO_Mapping_List.csv")
        if io_name:
            io_text = read_text(z, io_name)
            rows = list(csv.reader(io.StringIO(io_text)))
            print(f"✅ IO CSV 行数：{len(rows)}")
            for kw in ["Machine_Data.IN.bEstop", "Machine_Data.IN.bReset", "CylinderIO[1].bOriginSensor", "CylinderIO[1].bWorkValve"]:
                if kw in io_text:
                    print(f"✅ IO 包含：{kw}")
                else:
                    print(f"⚠️ IO 未明显包含：{kw}")
        else:
            ok = False

        print("\n========== 5. Sysmac 导入说明检查 ==========")
        guide_name = find_endswith(names, "Sysmac_Import_Guide.txt")
        if guide_name:
            guide = read_text(z, guide_name)
            for kw in ["Sysmac Studio", "导入顺序", "00_DUT_Struct_Generated.st", "00_Global_Variables_Generated.st", "IO_Mapping_List.csv"]:
                if kw in guide:
                    print(f"✅ 导入说明包含：{kw}")
                else:
                    print(f"❌ 导入说明缺少：{kw}")
                    ok = False
        else:
            ok = False

        print("\n========== 6. ST 质量报告检查 ==========")
        qr_name = find_endswith(names, "ST_Quality_Report.txt")
        if qr_name:
            qr = read_text(z, qr_name)
            for kw in ["ST Quality Report - V0.6.3", "OK:", "WARNING:", "ERROR:"]:
                if kw in qr:
                    print(f"✅ 质量报告包含：{kw}")
                else:
                    print(f"❌ 质量报告缺少：{kw}")
                    ok = False
        else:
            ok = False

        print("\n========== 7. manifest / validation 检查 ==========")
        manifest_name = find_endswith(names, "manifest.json")
        if manifest_name:
            manifest_text = read_text(z, manifest_name)
            manifest = json.loads(manifest_text)
            print("generator_version =", manifest.get("generator_version"))
            print("version =", manifest.get("version"))

            for kw in [
                "V0.6.3",
                "00_DUT_Struct_Generated.st",
                "00_Global_Variables_Generated.st",
                "IO_Mapping_List.csv",
                "Sysmac_Import_Guide.txt",
                "ST_Quality_Report.txt",
            ]:
                if kw in manifest_text:
                    print(f"✅ manifest 包含：{kw}")
                else:
                    print(f"❌ manifest 缺少：{kw}")
                    ok = False
        else:
            ok = False

        val_name = find_endswith(names, "validation_report.txt")
        if val_name:
            val_text = read_text(z, val_name)
            if "V0.6.3" in val_text:
                print("✅ validation_report 包含 V0.6.3")
            else:
                print("❌ validation_report 缺少 V0.6.3")
                ok = False
        else:
            ok = False

    print("\n========== V0.6.3 验收结论 ==========")
    if ok:
        print("✅ V0.6.3 Sysmac Studio 导入前工程规范增强通过")
    else:
        print("❌ V0.6.3 仍有问题，请把完整输出发给我")


if __name__ == "__main__":
    main()
'''
    write_file(CHECK_SCRIPT, content)


def main():
    print("========== 安装 V0.6.3 Product Core ==========")

    if not PROJECT_DIR.exists():
        print("❌ 项目目录不存在：", PROJECT_DIR)
        return

    if not GEN_DIR.exists():
        print("❌ company_generators 目录不存在：", GEN_DIR)
        return

    install_sysmac_export_generator()
    install_st_quality_checker()
    ok = patch_multi_station_generator()
    install_check_script()

    print("\n========== 安装结果 ==========")
    if ok:
        print("✅ V0.6.3 一键安装完成")
        print("下一步请运行：")
        print("python -m py_compile company_generators\\multi_station_project_generator.py")
        print("python check_v063_product_core.py")
    else:
        print("❌ V0.6.3 安装未完全成功，请把上面的输出发给我")


if __name__ == "__main__":
    main()