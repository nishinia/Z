from pathlib import Path

TARGET = Path("company_generators/device_ai_parser.py")
BACKUP = Path("company_generators/device_ai_parser_backup_before_v0511.py")

old_text = TARGET.read_text(encoding="utf-8")
BACKUP.write_text(old_text, encoding="utf-8")

new_text = r'''
import json
import re

from llm import call_llm


def extract_json(text: str) -> dict:
    text = text.strip()
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    match = re.search(r"\{[\s\S]*\}", text)

    if not match:
        raise ValueError("AI输出中没有找到JSON对象。")

    return json.loads(match.group(0))


def parse_project_info_from_text(requirement: str) -> dict:
    project_name = "AI_Device_Project_V051"
    plc = "Omron NJ501"
    description = "由整机中文需求自动解析生成的设备工程包。"

    m_project = re.search(r"项目名称[:：]\s*([A-Za-z0-9_\-\u4e00-\u9fa5]+)", requirement)
    if m_project:
        project_name = m_project.group(1).strip("。；;，,")

    if "NJ501" in requirement.upper():
        plc = "Omron NJ501"
    elif "NJ" in requirement.upper():
        plc = "Omron NJ Series"

    if requirement.strip():
        description = requirement.strip().splitlines()[0]

    return {
        "project_name": project_name,
        "plc": plc,
        "description": description
    }


def parse_cylinders_from_text(requirement: str) -> list[dict]:
    cylinders = []

    pattern = re.compile(
        r"(CY\d+)\s*"
        r"([^，。\n；;]*?气缸)"
        r"[，,]\s*原点\s*([^，。\n；;]+)"
        r"[，,]\s*动点\s*([^，。\n；;]+)"
        r"[，,]\s*原点阀\s*([^，。\n；;]+)"
        r"[，,]\s*动点阀\s*([^，。\n；;]+)",
        re.IGNORECASE
    )

    for match in pattern.finditer(requirement):
        instance = match.group(1).strip().upper()
        desc = match.group(2).strip()
        hp_sensor = match.group(3).strip()
        wp_sensor = match.group(4).strip()
        hp_valve = match.group(5).strip()
        wp_valve = match.group(6).strip()

        cylinders.append({
            "instance": instance,
            "data": f"Cylinder_Data.{instance}",
            "desc": desc,
            "hp_sensor": hp_sensor,
            "wp_sensor": wp_sensor,
            "hp_valve": hp_valve,
            "wp_valve": wp_valve,
            "on_ilc": "TRUE",
            "off_ilc": "TRUE"
        })

    return cylinders


def parse_station_info_from_text(requirement: str) -> dict:
    station_num = 1
    station_name = "S1_自动工站"
    program_name = "S1_Auto_Generated"

    m_station = re.search(r"S(\d+)\s*工站", requirement, re.IGNORECASE)
    if m_station:
        station_num = int(m_station.group(1))

    m_station_no = re.search(r"工站号\s*(\d+)", requirement)
    if m_station_no:
        station_num = int(m_station_no.group(1))

    station_name = f"S{station_num}_自动工站"
    program_name = f"S{station_num}_Auto_Generated"

    return {
        "program_name": program_name,
        "station_name": station_name,
        "station_num": station_num
    }


def get_flow_text(requirement: str) -> str:
    m_flow = re.search(r"流程[:：]([\s\S]+)", requirement)
    if not m_flow:
        return requirement

    flow_text = m_flow.group(1)

    # 去掉后面的通用说明，避免“每个动作步骤超时...”干扰流程识别
    flow_text = re.split(
        r"(每个动作步骤|每个步骤|超时|报警编号)",
        flow_text
    )[0]

    return flow_text


def build_cylinder_desc_map(cylinders: list[dict]) -> dict:
    result = {}

    for cyl in cylinders:
        instance = str(cyl.get("instance", "")).strip().upper()
        desc = str(cyl.get("desc", "")).strip()

        if instance:
            result[instance] = desc

    return result


def parse_flow_actions_from_text(requirement: str, cylinders: list[dict]) -> list[dict]:
    """
    V0.5.1.1 修复点：
    先按逗号/分号/句号切成短句，再判断动作。
    避免把“CY1动点到位后，CY2到动点”误判成 CY1 到动点。
    """
    flow_text = get_flow_text(requirement)
    cylinder_desc_map = build_cylinder_desc_map(cylinders)

    clauses = re.split(r"[，,；;。\n]", flow_text)

    actions = []

    for raw_clause in clauses:
        clause = raw_clause.strip()
        if not clause:
            continue

        cy_list = re.findall(r"CY\d+", clause, re.IGNORECASE)
        if not cy_list:
            continue

        # 每个短句只处理最后一个 CY，避免“CY1到位后 CY2动作”误判
        cy = cy_list[-1].upper()

        is_go_wp = "到动点" in clause
        is_go_hp = (
            "回原点" in clause
            or "回原位" in clause
            or "到原点" in clause
        )

        # “动点到位后 / 原点到位后”只是条件描述，不是动作
        if not is_go_wp and not is_go_hp:
            continue

        desc = cylinder_desc_map.get(cy, "")
        title_base = f"{cy}{desc}" if desc else cy

        if is_go_wp:
            actions.append({
                "cy": cy,
                "action": "go_wp",
                "title": f"{title_base}到动点",
                "command": f"Cylinder_Data.{cy}.Input.bAuto:=TRUE",
                "done": f"Cylinder_Data.{cy}.Output.bWP_Delay"
            })

        elif is_go_hp:
            actions.append({
                "cy": cy,
                "action": "go_hp",
                "title": f"{title_base}回原点",
                "command": f"Cylinder_Data.{cy}.Input.bAuto:=FALSE",
                "done": f"Cylinder_Data.{cy}.Output.bHP_Delay"
            })

    return actions


def build_station_config_from_text(
    requirement: str,
    cylinders: list[dict],
    ai_station_config: dict | None = None
) -> dict:
    station_info = parse_station_info_from_text(requirement)
    flow_actions = parse_flow_actions_from_text(requirement, cylinders)

    all_cy_instances = [c["instance"] for c in cylinders]

    safety_stop_actions = [
        f"Cylinder_Data.{cy}.Input.bAuto:=FALSE"
        for cy in all_cy_instances
    ]

    steps = []

    steps.append({
        "step": 0,
        "title": "INIT 初始化",
        "actions": safety_stop_actions.copy(),
        "next_condition": "bRunAble",
        "next_step": 10
    })

    steps.append({
        "step": 10,
        "title": "等待启动",
        "actions": [],
        "next_condition": "bRunAble AND Station[_StationNum].bRunning",
        "next_step": 20
    })

    if flow_actions:
        current_step = 20

        for index, item in enumerate(flow_actions):
            is_last = index == len(flow_actions) - 1

            step_item = {
                "step": current_step,
                "title": item["title"],
                "actions": [
                    item["command"]
                ],
                "next_condition": item["done"],
                "timeout_ms": 3000,
                "alarm_no": current_step
            }

            if is_last:
                step_item["is_complete"] = True
            else:
                step_item["next_step"] = current_step + 10

            steps.append(step_item)
            current_step += 10

    elif ai_station_config and ai_station_config.get("steps"):
        steps = ai_station_config.get("steps", steps)

    return {
        "program_name": station_info["program_name"],
        "station_name": station_info["station_name"],
        "station_num": station_info["station_num"],
        "safety_stop_actions": safety_stop_actions,
        "steps": steps
    }


def normalize_device_config(config: dict, requirement: str = "") -> dict:
    ai_project_info = config.get("project_info", {})
    ai_cylinder_config = config.get("cylinder_config", {})
    ai_station_config = config.get("station_config", {})

    project_info_from_text = parse_project_info_from_text(requirement)
    cylinders_from_text = parse_cylinders_from_text(requirement)

    project_info = {
        "project_name": project_info_from_text.get(
            "project_name",
            ai_project_info.get("project_name", "AI_Device_Project_V051")
        ),
        "plc": project_info_from_text.get(
            "plc",
            ai_project_info.get("plc", "Omron NJ501")
        ),
        "description": ai_project_info.get(
            "description",
            project_info_from_text.get("description", "由整机中文需求自动解析生成的设备工程包。")
        )
    }

    if cylinders_from_text:
        cylinder_config = {
            "cylinders": cylinders_from_text
        }
    else:
        cylinder_config = ai_cylinder_config or {
            "cylinders": []
        }

    station_config = build_station_config_from_text(
        requirement=requirement,
        cylinders=cylinder_config.get("cylinders", []),
        ai_station_config=ai_station_config
    )

    return {
        "project_info": project_info,
        "cylinder_config": cylinder_config,
        "station_config": station_config
    }


def parse_device_requirement(requirement: str) -> dict:
    prompt = f"""
你是欧姆龙 NJ501 自动化工程师，熟悉公司 PLC 模板。

你的任务：
把用户的整机中文需求解析成严格 JSON。
注意：你只能输出 JSON，不允许输出 ST 代码，不允许解释。

【用户整机需求】
{requirement}

【必须输出的 JSON 总结构】
{{
    "project_info": {{
        "project_name": "AI_Device_Project_V051",
        "plc": "Omron NJ501",
        "description": "项目说明"
    }},
    "cylinder_config": {{
        "cylinders": [
            {{
                "instance": "CY1",
                "data": "Cylinder_Data.CY1",
                "desc": "气缸描述",
                "hp_sensor": "原点感应器表达式",
                "wp_sensor": "动点感应器表达式",
                "hp_valve": "原点阀输出点",
                "wp_valve": "动点阀输出点",
                "on_ilc": "TRUE",
                "off_ilc": "TRUE"
            }}
        ]
    }},
    "station_config": {{
        "program_name": "S1_Auto_Generated",
        "station_name": "S1_工站名称",
        "station_num": 1,
        "safety_stop_actions": [
            "Cylinder_Data.CY1.Input.bAuto:=FALSE"
        ],
        "steps": []
    }}
}}

【要求】
1. 必须保留用户输入中的真实气缸名称。
2. 必须保留用户输入中的真实 IO 点位。
3. 用户写了 CY1，就必须输出 CY1。
4. 用户写了 CY2，就必须输出 CY2。
5. 用户没提供的 IO 点写 "TBD"。
6. 不允许输出 ST。
7. 不允许输出 Markdown。
8. 只能输出 JSON。
"""

    try:
        result = call_llm(prompt, temperature=0.0)
        config = extract_json(result)
    except Exception:
        config = {}

    return normalize_device_config(config, requirement=requirement)
'''

TARGET.write_text(new_text, encoding="utf-8")

print("device_ai_parser.py 已升级到 V0.5.1.1。")
print("原文件已备份为 company_generators/device_ai_parser_backup_before_v0511.py")