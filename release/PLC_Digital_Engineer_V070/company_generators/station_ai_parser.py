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


def parse_station_requirement(requirement: str) -> dict:
    prompt = f"""
你是欧姆龙NJ501自动化工程师，熟悉公司模板：
- 工站流程使用 Station[_StationNum].nAutoStep
- 气缸动作使用 Cylinder_Data.CYx.Input.bAuto
- 气缸到位判断使用 Cylinder_Data.CYx.Output.bWP_Delay 或 bHP_Delay
- 不允许直接写 Q 点
- 不允许自由写 ST
- 只允许输出 JSON

请把用户的工站需求解析成严格 JSON。

【用户需求】
{requirement}

【输出格式】
只能输出 JSON，不要解释，不要 Markdown，不要代码块。

JSON格式如下：
{{
    "program_name": "S1_Auto_Generated",
    "station_name": "S1_工站名称",
    "station_num": 1,
    "run_condition": "Machine_Data.IN.bEStop AND Machine_Data.IN.bSafety AND Machine_Data.IN.bAirOn",
    "reset_condition": "Machine_Data.bReset",
    "start_condition": "bRunAble AND Station[_StationNum].bRunning",
    "steps": [
        {{
            "step": 0,
            "title": "INIT 初始化",
            "actions": [
                "Cylinder_Data.CY1.Input.bAuto:=FALSE"
            ],
            "next_condition": "bRunAble",
            "next_step": 10
        }},
        {{
            "step": 10,
            "title": "等待启动",
            "actions": [],
            "next_condition": "bRunAble AND Station[_StationNum].bRunning",
            "next_step": 20
        }}
    ]
}}

【生成规则】
1. step 必须从 0、10、20、30 这种方式递增。
2. 必须包含 step 0 初始化。
3. 必须包含 step 10 等待启动。
4. 必须包含 step 999 报警停机。
5. 气缸到动点动作写：Cylinder_Data.CYx.Input.bAuto:=TRUE
6. 气缸回原点动作写：Cylinder_Data.CYx.Input.bAuto:=FALSE
7. 气缸动点到位条件写：Cylinder_Data.CYx.Output.bWP_Delay
8. 气缸原点到位条件写：Cylinder_Data.CYx.Output.bHP_Delay
9. 不允许输出 ST 代码。
10. 不允许输出解释。
11. 只能输出 JSON。
"""

    result = call_llm(prompt, temperature=0.0)
    return extract_json(result)