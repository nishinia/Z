from datetime import datetime
from pathlib import Path

from company_generators.cylinder_generator import validate_all_cylinders
from company_generators.station_generator import validate_station_config
from company_generators.symbols import load_company_symbols


REQUIRED_SYMBOL_KEYS = [
    "machine_estop",
    "machine_safety",
    "machine_air",
    "machine_reset",
    "station_step",
    "station_running",
    "station_estop",
    "station_alarm_base",
]


EXPECTED_TEMPLATE_FILES = [
    "FB_Cylinder.st",
    "Cylinder_Action.st",
    "MachineAlarm.st",
    "Machine_Init.st",
    "Servo_Action.st",
]


EXPECTED_OUTPUT_FILES = [
    "00_README.txt",
    "01_Cylinder_Action_Generated.st",
    "02_Station_Generated.st",
    "configs/cylinder_config.json",
    "configs/station_config.json",
    "configs/company_symbols.json",
]


def add_line(lines: list[str], text: str = ""):
    lines.append(text)


def check_cylinder_config(cylinder_config: dict) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []

    cylinders = cylinder_config.get("cylinders", [])

    if not cylinders:
        errors.append("气缸配置中没有 cylinders。")
        return errors, warnings

    errors.extend(validate_all_cylinders(cylinders))

    seen_instances = set()
    seen_data = set()

    for cyl in cylinders:
        instance = str(cyl.get("instance", "")).strip()
        data = str(cyl.get("data", "")).strip()

        if instance in seen_instances:
            errors.append(f"气缸实例重复：{instance}")
        seen_instances.add(instance)

        if data in seen_data:
            warnings.append(f"气缸数据对象重复：{data}")
        seen_data.add(data)

        for field in ["hp_sensor", "wp_sensor", "hp_valve", "wp_valve"]:
            value = str(cyl.get(field, "")).strip()
            if value.upper() == "TBD":
                errors.append(f"{instance} 的 {field} 仍为 TBD，未填写实际 IO 点。")

        if cyl.get("on_ilc") is None:
            warnings.append(f"{instance} 未设置 on_ilc，默认可能不明确。")

        if cyl.get("off_ilc") is None:
            warnings.append(f"{instance} 未设置 off_ilc，默认可能不明确。")

    return errors, warnings


def check_station_config(station_config: dict) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []

    errors.extend(validate_station_config(station_config))

    steps = station_config.get("steps", [])
    if not steps:
        return errors, warnings

    step_numbers = [s.get("step") for s in steps if s.get("step") is not None]
    step_set = set(step_numbers)

    if 0 not in step_set:
        errors.append("工站缺少 step 0 初始化。")

    if 10 not in step_set:
        warnings.append("工站建议保留 step 10 等待启动。")

    alarm_nos = []
    alarm_bits = []

    for step in steps:
        step_no = step.get("step")
        title = step.get("title", "")

        if step_no == 999:
            continue

        next_step = step.get("next_step")
        is_complete = step.get("is_complete", False)

        if not is_complete and next_step is not None and next_step not in step_set and next_step != 999:
            errors.append(f"step {step_no} 的 next_step={next_step} 不存在。")

        timeout_ms = step.get("timeout_ms")
        alarm_no = step.get("alarm_no")
        alarm_bit = step.get("alarm_bit")

        if timeout_ms is not None:
            if alarm_no is None and not alarm_bit:
                errors.append(f"step {step_no} 配置了 timeout_ms，但没有 alarm_no 或 alarm_bit。")

            try:
                timeout_int = int(timeout_ms)
                if timeout_int < 500:
                    warnings.append(f"step {step_no} 超时时间 {timeout_int}ms 可能过短。")
                if timeout_int > 60000:
                    warnings.append(f"step {step_no} 超时时间 {timeout_int}ms 可能过长。")
            except Exception:
                errors.append(f"step {step_no} timeout_ms 不是整数。")

        if alarm_no is not None:
            alarm_nos.append(alarm_no)

        if alarm_bit:
            alarm_bits.append(alarm_bit)

        actions = step.get("actions", [])
        if not actions and step_no not in [0, 10]:
            warnings.append(f"step {step_no}（{title}）没有动作 actions。")

    duplicated_alarm_nos = sorted({x for x in alarm_nos if alarm_nos.count(x) > 1})
    for alarm_no in duplicated_alarm_nos:
        errors.append(f"报警编号重复：alarm_no={alarm_no}")

    duplicated_alarm_bits = sorted({x for x in alarm_bits if alarm_bits.count(x) > 1})
    for alarm_bit in duplicated_alarm_bits:
        errors.append(f"报警位重复：{alarm_bit}")

    has_complete_step = any(step.get("is_complete", False) for step in steps)
    if not has_complete_step:
        warnings.append("未检测到 is_complete=true 的完成步，流程可能不会正常结束。")

    return errors, warnings


def check_company_symbols() -> tuple[list[str], list[str]]:
    errors = []
    warnings = []

    symbols = load_company_symbols()

    for key in REQUIRED_SYMBOL_KEYS:
        if key not in symbols or not str(symbols[key]).strip():
            errors.append(f"company_symbols 缺少字段：{key}")

    machine_estop = symbols.get("machine_estop", "")
    if "bEStop" in machine_estop:
        warnings.append("machine_estop 当前为 bEStop，请确认公司模板实际大小写是否一致。")
    if "bEstop" in machine_estop:
        warnings.append("machine_estop 当前为 bEstop，请确认公司模板实际大小写是否一致。")

    return errors, warnings


def check_package_files(package_dir: Path | None) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []

    if package_dir is None:
        warnings.append("未提供 package_dir，跳过工程包文件存在性检查。")
        return errors, warnings

    if not package_dir.exists():
        errors.append(f"工程包目录不存在：{package_dir}")
        return errors, warnings

    for rel_path in EXPECTED_OUTPUT_FILES:
        file_path = package_dir / rel_path
        if not file_path.exists():
            errors.append(f"工程包缺少文件：{rel_path}")

    template_dir = package_dir / "template_source"

    if not template_dir.exists():
        warnings.append("工程包缺少 template_source 目录。")
    else:
        for name in EXPECTED_TEMPLATE_FILES:
            if not (template_dir / name).exists():
                warnings.append(f"template_source 缺少参考模板：{name}")

    return errors, warnings


def build_validation_report(
    cylinder_config: dict,
    station_config: dict,
    project_info: dict,
    package_dir: str | Path | None = None
) -> str:
    package_path = Path(package_dir) if package_dir else None

    errors = []
    warnings = []

    cyl_errors, cyl_warnings = check_cylinder_config(cylinder_config)
    station_errors, station_warnings = check_station_config(station_config)
    symbol_errors, symbol_warnings = check_company_symbols()
    file_errors, file_warnings = check_package_files(package_path)

    errors.extend(cyl_errors)
    errors.extend(station_errors)
    errors.extend(symbol_errors)
    errors.extend(file_errors)

    warnings.extend(cyl_warnings)
    warnings.extend(station_warnings)
    warnings.extend(symbol_warnings)
    warnings.extend(file_warnings)

    lines = []

    add_line(lines, "PLC数字工程师 V0.4.2 自动校验报告")
    add_line(lines, "=" * 60)
    add_line(lines, f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    add_line(lines, f"项目名称：{project_info.get('project_name', 'UNKNOWN')}")
    add_line(lines, f"PLC：{project_info.get('plc', 'UNKNOWN')}")
    add_line(lines, "")

    add_line(lines, "一、总体结论")
    add_line(lines, "-" * 60)

    if errors:
        add_line(lines, f"结果：不通过（发现 {len(errors)} 个错误，{len(warnings)} 个警告）")
    elif warnings:
        add_line(lines, f"结果：有警告（0 个错误，{len(warnings)} 个警告）")
    else:
        add_line(lines, "结果：基础校验通过（0 个错误，0 个警告）")

    add_line(lines, "")

    add_line(lines, "二、配置统计")
    add_line(lines, "-" * 60)
    add_line(lines, f"气缸数量：{len(cylinder_config.get('cylinders', []))}")
    add_line(lines, f"工站步骤数量：{len(station_config.get('steps', []))}")
    add_line(lines, f"工程包目录：{str(package_path) if package_path else '未提供'}")
    add_line(lines, "")

    add_line(lines, "三、错误列表")
    add_line(lines, "-" * 60)

    if errors:
        for index, err in enumerate(errors, start=1):
            add_line(lines, f"{index}. {err}")
    else:
        add_line(lines, "无错误。")

    add_line(lines, "")

    add_line(lines, "四、警告列表")
    add_line(lines, "-" * 60)

    if warnings:
        for index, warn in enumerate(warnings, start=1):
            add_line(lines, f"{index}. {warn}")
    else:
        add_line(lines, "无警告。")

    add_line(lines, "")

    add_line(lines, "五、人工复核建议")
    add_line(lines, "-" * 60)
    add_line(lines, "1. 检查所有 IO 点位是否与电气图一致。")
    add_line(lines, "2. 检查 Cylinder_Data.CYx 是否已在全局变量中定义。")
    add_line(lines, "3. 检查 Station[_StationNum] 的工站号是否与 HMI / 报警表一致。")
    add_line(lines, "4. 检查 Machine_Data.IN 字段大小写是否与公司模板一致。")
    add_line(lines, "5. 检查报警编号是否符合公司报警表规范。")
    add_line(lines, "6. 在 Sysmac Studio 中编译后，再做仿真和空载测试。")
    add_line(lines, "7. 急停、安全门、光栅等安全回路必须由硬件安全回路保证。")

    return "\n".join(lines)