import json
import re
from pathlib import Path

from company_generators.symbols import (
    load_company_symbols,
    build_default_run_condition,
    build_alarm_bit
)


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "configs" / "sample_station.json"
OUTPUT_PATH = BASE_DIR / "output" / "Station_Generated.st"


def ensure_semicolon(line: str) -> str:
    line = str(line).strip()
    if not line:
        return ""
    if line.endswith(";"):
        return line
    return line + ";"


def time_ms_to_st(timeout_ms: int) -> str:
    return f"T#{int(timeout_ms)}MS"


def resolve_alarm_bit(step_item: dict, symbols: dict) -> str:
    if step_item.get("alarm_bit"):
        return step_item["alarm_bit"]

    if step_item.get("alarm_no") is not None:
        return build_alarm_bit(symbols, step_item["alarm_no"])

    return ""


def collect_cylinder_stop_actions(config: dict) -> list[str]:
    signals = set()

    for step in config.get("steps", []):
        for action in step.get("actions", []):
            match = re.search(r"(Cylinder_Data\.CY\d+\.Input\.bAuto)\s*:=", action)
            if match:
                signals.add(match.group(1))

    return [f"{sig}:=FALSE" for sig in sorted(signals)]


def collect_alarm_bits(config: dict, symbols: dict) -> list[str]:
    alarm_bits = []

    for step in config.get("steps", []):
        alarm_bit = resolve_alarm_bit(step, symbols)
        if alarm_bit and alarm_bit not in alarm_bits:
            alarm_bits.append(alarm_bit)

    return alarm_bits


def validate_station_config(config: dict) -> list[str]:
    errors = []

    required_top_fields = [
        "program_name",
        "station_name",
        "station_num",
        "steps"
    ]

    for field in required_top_fields:
        if field not in config:
            errors.append(f"缺少顶层字段：{field}")

    steps = config.get("steps", [])

    if not isinstance(steps, list) or not steps:
        errors.append("steps 必须是非空数组。")
        return errors

    seen_steps = set()

    for item in steps:
        step = item.get("step")

        if step is None:
            errors.append("某个 step 缺少 step 编号。")
            continue

        if step in seen_steps:
            errors.append(f"step 编号重复：{step}")
        else:
            seen_steps.add(step)

        if "title" not in item:
            errors.append(f"step {step} 缺少 title。")

        if "actions" not in item:
            errors.append(f"step {step} 缺少 actions。")

        if step != 999:
            if "next_condition" not in item:
                errors.append(f"step {step} 缺少 next_condition。")

            if not item.get("is_complete", False):
                if "next_step" not in item:
                    errors.append(f"step {step} 缺少 next_step。")

        timeout_ms = item.get("timeout_ms")
        alarm_bit = item.get("alarm_bit")
        alarm_no = item.get("alarm_no")

        if timeout_ms is not None:
            try:
                timeout_ms = int(timeout_ms)
                if timeout_ms <= 0:
                    errors.append(f"step {step} 的 timeout_ms 必须大于 0。")
            except Exception:
                errors.append(f"step {step} 的 timeout_ms 必须是整数。")

            if not alarm_bit and alarm_no is None:
                errors.append(f"step {step} 设置了 timeout_ms，但缺少 alarm_bit 或 alarm_no。")

    if 0 not in seen_steps:
        errors.append("缺少 step 0 初始化步骤。")

    if 10 not in seen_steps:
        errors.append("建议包含 step 10 等待启动步骤。")

    return errors


def render_actions(actions: list[str], indent: str = "        ") -> list[str]:
    lines = []

    for action in actions:
        action = ensure_semicolon(action)
        if action:
            lines.append(indent + action)

    return lines


def render_station_program(config: dict) -> str:
    symbols = load_company_symbols()

    program_name = config["program_name"]
    station_name = config["station_name"]
    station_num = config["station_num"]

    run_condition = config.get("run_condition") or build_default_run_condition(symbols)
    reset_condition = config.get("reset_condition") or symbols["machine_reset"]

    station_step = symbols["station_step"]
    station_running = symbols["station_running"]
    station_estop = symbols["station_estop"]

    steps = config["steps"]
    normal_steps = [s for s in steps if s.get("step") != 999]

    safety_stop_actions = config.get("safety_stop_actions")
    if not safety_stop_actions:
        safety_stop_actions = collect_cylinder_stop_actions(config)

    alarm_bits = collect_alarm_bits(config, symbols)

    timeout_steps = [
        s for s in normal_steps
        if s.get("timeout_ms") is not None and resolve_alarm_bit(s, symbols)
    ]

    lines = []

    lines.append("// ==================================================")
    lines.append(f"// {program_name} - 公司工站模板生成版 V0.3.3")
    lines.append(f"// 工站名称：{station_name}")
    lines.append("// 功能：自动流程 / 完成复位 / 超时报警 / 安全停机 / 公司命名配置化")
    lines.append("// 由 PLC数字工程师 根据公司模板自动生成")
    lines.append("// ==================================================")
    lines.append("")
    lines.append(f"PROGRAM {program_name}")
    lines.append("")
    lines.append("VAR")
    lines.append(f"    _StationNum : INT := {station_num};")
    lines.append("    bRunAble    : BOOL;")

    for step in timeout_steps:
        step_num = step["step"]
        lines.append(f"    T_Step_{step_num}   : TON;")

    lines.append("END_VAR")
    lines.append("")
    lines.append("")
    lines.append("// ==================================================")
    lines.append("// 工站运行条件")
    lines.append("// ==================================================")
    lines.append(f"bRunAble := {run_condition};")
    lines.append("")
    lines.append("")
    lines.append("// ==================================================")
    lines.append("// Step 超时计时器")
    lines.append("// ==================================================")

    if timeout_steps:
        for step in timeout_steps:
            step_num = step["step"]
            timeout_ms = int(step["timeout_ms"])
            lines.append(
                f"T_Step_{step_num}(IN := {station_step} = {step_num}, PT := {time_ms_to_st(timeout_ms)});"
            )
    else:
        lines.append("// 当前配置未启用 step timeout。")

    lines.append("")
    lines.append("")
    lines.append("// ==================================================")
    lines.append("// 安全停机处理")
    lines.append("// ==================================================")
    lines.append("IF NOT bRunAble THEN")

    for action in safety_stop_actions:
        lines.append("    " + ensure_semicolon(action))

    lines.append(f"    {station_estop} := TRUE;")
    lines.append(f"    {station_running} := FALSE;")
    lines.append(f"    {station_step} := 999;")
    lines.append("END_IF;")
    lines.append("")
    lines.append("")
    lines.append("// ==================================================")
    lines.append("// 复位处理")
    lines.append("// ==================================================")
    lines.append(f"IF {reset_condition} THEN")
    lines.append(f"    {station_estop} := FALSE;")

    for alarm_bit in alarm_bits:
        lines.append(f"    {alarm_bit} := FALSE;")

    lines.append("END_IF;")
    lines.append("")
    lines.append("")
    lines.append("// ==================================================")
    lines.append("// 工站自动流程")
    lines.append("// ==================================================")
    lines.append(f"CASE {station_step} OF")
    lines.append("")

    for item in normal_steps:
        step = item["step"]
        title = item.get("title", "")
        actions = item.get("actions", [])
        next_condition = item.get("next_condition", "")
        next_step = item.get("next_step", None)
        is_complete = item.get("is_complete", False)
        timeout_ms = item.get("timeout_ms")
        alarm_bit = resolve_alarm_bit(item, symbols)

        lines.append(f"    {step}: // {title}")

        action_lines = render_actions(actions, indent="        ")
        if action_lines:
            lines.extend(action_lines)
        else:
            lines.append("        // No action")

        lines.append("")

        if timeout_ms is not None and alarm_bit:
            lines.append(f"        IF T_Step_{step}.Q THEN")
            lines.append(f"            {alarm_bit} := TRUE;")

            for action in safety_stop_actions:
                lines.append("            " + ensure_semicolon(action))

            lines.append(f"            {station_running} := FALSE;")
            lines.append(f"            {station_step} := 999;")
            lines.append(f"        ELSIF {next_condition} THEN")

            if is_complete:
                lines.append(f"            {station_running} := FALSE;")
                lines.append(f"            {station_step} := 10;")
            else:
                lines.append(f"            {station_step} := {next_step};")

            lines.append("        END_IF;")

        elif next_condition:
            lines.append(f"        IF {next_condition} THEN")

            if is_complete:
                lines.append(f"            {station_running} := FALSE;")
                lines.append(f"            {station_step} := 10;")
            else:
                lines.append(f"            {station_step} := {next_step};")

            lines.append("        END_IF;")

        lines.append("")

    lines.append("    999: // ERROR 报警停机")

    for action in safety_stop_actions:
        lines.append("        " + ensure_semicolon(action))

    lines.append(f"        {station_running} := FALSE;")
    lines.append("")
    lines.append(f"        IF {reset_condition} AND bRunAble THEN")
    lines.append(f"            {station_estop} := FALSE;")
    lines.append(f"            {station_step} := 10;")
    lines.append("        END_IF;")
    lines.append("")
    lines.append("    ELSE")
    lines.append(f"        {station_step} := 999;")
    lines.append("")
    lines.append("END_CASE;")
    lines.append("")
    lines.append("END_PROGRAM")
    lines.append("")

    return "\n".join(lines)


def load_station_config(path: str | Path = CONFIG_PATH) -> dict:
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    config = load_station_config()
    errors = validate_station_config(config)

    if errors:
        print("配置存在问题：")
        for err in errors:
            print(" -", err)
        return

    code = render_station_program(config)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(code, encoding="utf-8")

    print("工站程序已生成：")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()