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
    project_name = "AI_Device_Project_V061"
    plc = "Omron NJ501"
    description = "由整机中文需求自动解析生成的多工站工程包。"

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


def build_cylinder_desc_map(cylinders: list[dict]) -> dict:
    result = {}

    for cyl in cylinders:
        instance = str(cyl.get("instance", "")).strip().upper()
        desc = str(cyl.get("desc", "")).strip()

        if instance:
            result[instance] = desc

    return result


def split_station_blocks(requirement: str) -> list[dict]:
    """
    识别类似：
    S1上料工站，工站号1。流程：...
    S2分拣工站，工站号2。流程：...
    """
    pattern = re.compile(
        r"(S\d+)\s*([^，。\n；;]*?工站)(?:[，,。\s]*工站号\s*(\d+))?",
        re.IGNORECASE
    )

    matches = list(pattern.finditer(requirement))

    blocks = []

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(requirement)

        station_code = match.group(1).upper()
        station_desc = match.group(2).strip()
        station_num_text = match.group(3)

        station_num = int(re.sub(r"\D", "", station_code))

        if station_num_text:
            station_num = int(station_num_text)

        block_text = requirement[start:end].strip()

        blocks.append({
            "station_code": station_code,
            "station_desc": station_desc,
            "station_num": station_num,
            "block_text": block_text
        })

    return blocks


def get_flow_text(block_text: str) -> str:
    m_flow = re.search(r"流程[:：]([\s\S]+)", block_text)
    if not m_flow:
        return block_text

    flow_text = m_flow.group(1)

    flow_text = re.split(
        r"(每个动作步骤|每个步骤|超时|报警编号|备注[:：])",
        flow_text
    )[0]

    return flow_text


def parse_flow_actions_from_block(block_text: str, cylinders: list[dict]) -> list[dict]:
    """
    先按短句切分，再识别 CYx 到动点 / 回原点。
    避免“CY1到位后，CY2动作”被误判。
    """
    flow_text = get_flow_text(block_text)
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

        cy = cy_list[-1].upper()

        is_go_wp = "到动点" in clause
        is_go_hp = (
            "回原点" in clause
            or "回原位" in clause
            or "到原点" in clause
        )

        if not is_go_wp and not is_go_hp:
            continue

        desc = cylinder_desc_map.get(cy, "")
        title_base = f"{cy}{desc}" if desc else cy

        if is_go_wp:
            actions.append({
                "cy": cy,
                "title": f"{title_base}到动点",
                "command": f"Cylinder_Data.{cy}.Input.bAuto:=TRUE",
                "done": f"Cylinder_Data.{cy}.Output.bWP_Delay"
            })

        elif is_go_hp:
            actions.append({
                "cy": cy,
                "title": f"{title_base}回原点",
                "command": f"Cylinder_Data.{cy}.Input.bAuto:=FALSE",
                "done": f"Cylinder_Data.{cy}.Output.bHP_Delay"
            })

    return actions


def build_station_config_from_block(block: dict, cylinders: list[dict]) -> dict:
    station_code = block["station_code"]
    station_num = block["station_num"]
    station_desc = block["station_desc"]
    block_text = block["block_text"]

    program_name = f"{station_code}_Auto_Generated"
    station_name = f"{station_code}_{station_desc}"

    flow_actions = parse_flow_actions_from_block(block_text, cylinders)

    used_cys = []

    for item in flow_actions:
        cy = item["cy"]
        if cy not in used_cys:
            used_cys.append(cy)

    if not used_cys:
        used_cys = [
            str(cyl.get("instance", "")).strip().upper()
            for cyl in cylinders
            if cyl.get("instance")
        ]

    safety_stop_actions = [
        f"Cylinder_Data.{cy}.Input.bAuto:=FALSE"
        for cy in used_cys
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

    return {
        "program_name": program_name,
        "station_name": station_name,
        "station_num": station_num,
        "safety_stop_actions": safety_stop_actions,
        "steps": steps
    }


def normalize_multi_station_config(config: dict, requirement: str) -> dict:
    ai_project_info = config.get("project_info", {})
    ai_cylinder_config = config.get("cylinder_config", {})
    ai_station_configs = config.get("station_configs", [])

    project_info_from_text = parse_project_info_from_text(requirement)
    cylinders_from_text = parse_cylinders_from_text(requirement)

    project_info = {
        "project_name": project_info_from_text.get(
            "project_name",
            ai_project_info.get("project_name", "AI_Device_Project_V061")
        ),
        "plc": project_info_from_text.get(
            "plc",
            ai_project_info.get("plc", "Omron NJ501")
        ),
        "description": ai_project_info.get(
            "description",
            project_info_from_text.get("description", "由整机中文需求自动解析生成的多工站工程包。")
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

    station_blocks = split_station_blocks(requirement)

    station_configs = []

    if station_blocks:
        for block in station_blocks:
            station_configs.append(
                build_station_config_from_block(
                    block=block,
                    cylinders=cylinder_config.get("cylinders", [])
                )
            )
    elif ai_station_configs:
        station_configs = ai_station_configs

    return {
        "project_info": project_info,
        "cylinder_config": cylinder_config,
        "station_configs": station_configs
    }


def parse_multi_station_requirement(requirement: str) -> dict:
    prompt = f"""
你是欧姆龙 NJ501 自动化工程师，熟悉公司 PLC 模板。

你的任务：
把用户的整机中文需求解析成严格 JSON。
注意：只能输出 JSON，不允许输出 ST 代码，不允许解释。

【用户整机需求】
{requirement}

【必须输出 JSON 结构】
{{
    "project_info": {{
        "project_name": "AI_Device_Project_V061",
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
    "station_configs": [
        {{
            "program_name": "S1_Auto_Generated",
            "station_name": "S1_工站名称",
            "station_num": 1,
            "safety_stop_actions": [
                "Cylinder_Data.CY1.Input.bAuto:=FALSE"
            ],
            "steps": []
        }}
    ]
}}

【规则】
1. S1、S2、S3 要解析成多个 station_configs。
2. 每个工站独立生成 program_name。
3. 气缸动作到动点写 bAuto:=TRUE。
4. 气缸回原点写 bAuto:=FALSE。
5. 到位条件使用 bWP_Delay 或 bHP_Delay。
6. 用户没提供 IO 写 TBD。
7. 不允许输出 ST。
8. 不允许 Markdown。
9. 只能输出 JSON。
"""

    try:
        result = call_llm(prompt, temperature=0.0)
        config = extract_json(result)
    except Exception:
        config = {}

    return normalize_multi_station_config(
        config=config,
        requirement=requirement
    )