import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "configs" / "sample_cylinders.json"
OUTPUT_PATH = BASE_DIR / "output" / "Cylinder_Action_Generated.st"


def normalize_expr(value: str) -> str:
    """
    清理 AI 输出的表达式，让它更接近公司模板风格。
    例如：
    (I1_0 AND I1_3) -> I1_0 AND I1_3
    """
    if value is None:
        return ""

    text = str(value).strip()

    # 去掉首尾多余空格
    text = text.strip()

    # 如果整体被一层括号包住，就去掉
    if text.startswith("(") and text.endswith(")"):
        inner = text[1:-1].strip()

        # 简单判断括号内没有复杂嵌套时才去掉
        if inner.count("(") == inner.count(")"):
            text = inner

    return text


def validate_cylinder(cyl: dict) -> list[str]:
    errors = []

    required_fields = [
        "instance",
        "data",
        "hp_sensor",
        "wp_sensor",
        "hp_valve",
        "wp_valve"
    ]

    for field in required_fields:
        if field not in cyl or not str(cyl[field]).strip():
            errors.append(f"缺少字段：{field}")

    instance = str(cyl.get("instance", "")).strip()
    data = str(cyl.get("data", "")).strip()

    if not instance.startswith("CY"):
        errors.append(f"气缸实例名建议使用 CY 开头：{instance}")

    if not data.startswith("Cylinder_Data."):
        errors.append(f"气缸数据建议使用 Cylinder_Data.CYx 格式：{data}")

    for field in ["hp_sensor", "wp_sensor", "hp_valve", "wp_valve"]:
        value = str(cyl.get(field, "")).strip()
        if value.upper() == "TBD":
            errors.append(f"{field} 还没有填写实际 IO 点位。")

    return errors


def validate_all_cylinders(cylinders: list[dict]) -> list[str]:
    errors = []
    seen_instances = set()

    for cyl in cylinders:
        instance = str(cyl.get("instance", "")).strip()

        if instance in seen_instances:
            errors.append(f"气缸实例重复：{instance}")
        else:
            seen_instances.add(instance)

        item_errors = validate_cylinder(cyl)
        for err in item_errors:
            errors.append(f"{instance or 'UNKNOWN'}：{err}")

    return errors


def render_cylinder_action(cylinders: list[dict]) -> str:
    lines = []

    lines.append("// ==================================================")
    lines.append("// Cylinder_Action - 公司模板生成版")
    lines.append("// 由 PLC数字工程师 根据公司模板自动生成")
    lines.append("// ==================================================")
    lines.append("")

    for cyl in cylinders:
        instance = normalize_expr(cyl["instance"])
        data = normalize_expr(cyl["data"])
        desc = normalize_expr(cyl.get("desc", ""))
        hp_sensor = normalize_expr(cyl["hp_sensor"])
        wp_sensor = normalize_expr(cyl["wp_sensor"])
        hp_valve = normalize_expr(cyl["hp_valve"])
        wp_valve = normalize_expr(cyl["wp_valve"])
        on_ilc = normalize_expr(cyl.get("on_ilc", "TRUE"))
        off_ilc = normalize_expr(cyl.get("off_ilc", "TRUE"))

        lines.append(f"//{instance}_{desc}")
        lines.append(
            f"{instance}(CylinderData:={data}, Machine:=Machine_Data,"
        )
        lines.append(
            f"        bHP_Sensor:={hp_sensor}, bWP_Sensor:={wp_sensor},"
        )
        lines.append(
            f"        bHP_Valve=>{hp_valve}, bWP_Valve=>{wp_valve});"
        )
        lines.append(f"{data}.Input.bOnILC:={on_ilc};")
        lines.append(f"{data}.Input.bOffILC:={off_ilc};")
        lines.append("")

    return "\n".join(lines)


def load_cylinders() -> list[dict]:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return data.get("cylinders", [])


def main():
    cylinders = load_cylinders()

    errors = validate_all_cylinders(cylinders)

    if errors:
        print("配置存在问题：")
        for err in errors:
            print(" -", err)
        return

    code = render_cylinder_action(cylinders)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(code, encoding="utf-8")

    print("气缸动作程序已生成：")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()