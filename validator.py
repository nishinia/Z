import re


def validate_code(code: str) -> list[str]:
    warnings = []

    required_keywords = [
        "CASE",
        "END_CASE",
        "IF",
        "END_IF"
    ]

    for keyword in required_keywords:
        if keyword not in code:
            warnings.append(f"警告：代码中未检测到关键字 {keyword}")

    if "```" in code:
        warnings.append("警告：检测到 Markdown 代码块符号，请清理 ```。")

    if "EStop" not in code and "急停" not in code:
        warnings.append("警告：未明显检测到急停逻辑。")

    if "Alarm" not in code and "ALM_" not in code:
        warnings.append("警告：未明显检测到报警逻辑。")

    if "Reset" not in code:
        warnings.append("警告：未明显检测到复位逻辑。")

    if "Y_" in code and ("EStopOK" not in code and "DoorOK" not in code):
        warnings.append("警告：检测到输出点，但安全互锁可能不完整。")

    banned_calls = [
        "FB_Alarm(",
        "Y_StopAllOutputs(",
        "FB_CheckFullBin(",
        "CheckSensor(",
        "StopAll("
    ]

    for call in banned_calls:
        if call in code:
            warnings.append(f"严重警告：检测到未定义/禁止调用：{call}")

    allowed_fb_calls = [
        "FB_Conveyor",
        "FB_Scanner",
        "FB_Diverter",
        "FB_AlarmManager"
    ]

    function_calls = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", code)

    for func in function_calls:
        if func.startswith("FB_") and func not in allowed_fb_calls:
            warnings.append(f"警告：检测到可能未定义的函数块调用：{func}()")

        if func.startswith("Y_"):
            warnings.append(f"警告：输出点不应该像函数一样调用：{func}()")

    return warnings