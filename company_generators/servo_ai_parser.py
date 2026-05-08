import re


def _to_float(text, default=0.0):
    try:
        return float(str(text).replace(",", "").strip())
    except Exception:
        return default


def _find_default_velocity(text):
    patterns = [
        r"速度\s*([0-9]+(?:\.[0-9]+)?)\s*(?:mm/s|毫米/秒|mm每秒)?",
        r"运行速度\s*([0-9]+(?:\.[0-9]+)?)",
        r"定位速度\s*([0-9]+(?:\.[0-9]+)?)",
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return _to_float(m.group(1), 100.0)

    return 100.0


def _find_default_acc(text):
    patterns = [
        r"加速度\s*([0-9]+(?:\.[0-9]+)?)",
        r"加减速\s*([0-9]+(?:\.[0-9]+)?)",
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return _to_float(m.group(1), 500.0)

    return 500.0


def _find_points(text):
    points = []

    patterns = [
        r"点位\s*(\d+)\s*(?:为|是|:|：)?\s*([\u4e00-\u9fa5A-Za-z0-9_]+)?\s*([\-0-9]+(?:\.[0-9]+)?)\s*mm",
        r"位置\s*(\d+)\s*(?:为|是|:|：)?\s*([\u4e00-\u9fa5A-Za-z0-9_]+)?\s*([\-0-9]+(?:\.[0-9]+)?)\s*mm",
        r"P\s*(\d+)\s*(?:为|是|:|：)?\s*([\u4e00-\u9fa5A-Za-z0-9_]+)?\s*([\-0-9]+(?:\.[0-9]+)?)\s*mm",
    ]

    for pattern in patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            point_no = int(m.group(1))
            point_name = m.group(2) or f"P{point_no}"
            position = _to_float(m.group(3), 0.0)

            points.append({
                "point_no": point_no,
                "point_name": point_name,
                "position": position,
                "unit": "mm",
            })

    # 去重
    result = []
    seen = set()

    for p in sorted(points, key=lambda x: x["point_no"]):
        if p["point_no"] in seen:
            continue

        seen.add(p["point_no"])
        result.append(p)

    return result


def _find_axis_names(text):
    names = []

    # 常见写法：X轴伺服 / 一个X轴伺服 / X轴 / Y轴
    for m in re.finditer(r"([XYZUVWABC])\s*轴\s*(?:伺服|轴)?", text, re.IGNORECASE):
        axis = m.group(1).upper()
        if axis not in names:
            names.append(axis)

    # 中文描述：搬运轴、升降轴、横移轴
    chinese_axis_patterns = [
        "搬运轴",
        "升降轴",
        "横移轴",
        "旋转轴",
        "输送轴",
        "压装轴",
    ]

    for name in chinese_axis_patterns:
        if name in text and name not in names:
            names.append(name)

    return names


def parse_servo_requirement(requirement_text: str) -> dict:
    text = requirement_text or ""

    has_servo = any(k in text for k in ["伺服", "轴", "回零", "点位", "定位", "绝对位置", "MoveAbs"])

    if not has_servo:
        return {
            "axes": []
        }

    axis_names = _find_axis_names(text)

    if not axis_names:
        axis_names = ["X"]

    velocity = _find_default_velocity(text)
    acc = _find_default_acc(text)
    points = _find_points(text)

    if not points:
        points = [
            {
                "point_no": 1,
                "point_name": "上料位",
                "position": 0.0,
                "unit": "mm",
            },
            {
                "point_no": 2,
                "point_name": "工作位",
                "position": 100.0,
                "unit": "mm",
            },
        ]

    axes = []

    for i, axis_name in enumerate(axis_names, start=1):
        display_name = axis_name if str(axis_name).endswith("轴") else f"{axis_name}轴"

        axis_type = "rotary" if "旋转" in display_name else "linear"

        axes.append({
            "axis_id": f"AX{i}",
            "axis_name": display_name,
            "axis_type": axis_type,
            "unit": "deg" if axis_type == "rotary" else "mm",
            "home_required": "回零" in text or "原点" in text,
            "default_velocity": velocity,
            "default_acceleration": acc,
            "default_deceleration": acc,
            "positive_limit": "",
            "negative_limit": "",
            "home_sensor": "",
            "servo_alarm": "",
            "points": points,
            "sequence": [
                "ServoOn",
                "Home",
                "MoveAbs",
                "Done",
            ],
        })

    return {
        "axes": axes
    }
