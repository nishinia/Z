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
