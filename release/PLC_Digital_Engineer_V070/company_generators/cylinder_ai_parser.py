import json
import re

from llm import call_llm


def extract_json(text: str) -> dict:
    """
    从模型输出中提取 JSON。
    防止模型带上 ```json 之类的 Markdown。
    """
    text = text.strip()
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    match = re.search(r"\{[\s\S]*\}", text)

    if not match:
        raise ValueError("AI输出中没有找到JSON对象。")

    json_text = match.group(0)
    return json.loads(json_text)


def parse_cylinder_requirement(requirement: str) -> dict:
    prompt = f"""
你是欧姆龙NJ501自动化工程师。

请把用户的气缸需求解析成严格JSON。

【用户需求】
{requirement}

【输出格式】
只能输出JSON，不要解释，不要Markdown，不要代码块。

JSON格式如下：
{{
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
}}

【规则】
1. instance 必须是 CY1、CY2、CY3 这种格式。
2. data 必须是 Cylinder_Data.CY1、Cylinder_Data.CY2 这种格式。
3. hp_sensor 是原点感应器。
4. wp_sensor 是动点感应器。
5. hp_valve 是原点阀。
6. wp_valve 是动点阀。
7. 如果用户没有提供某个IO点，就写成 TBD。
8. 不允许输出ST代码。
9. 不允许输出解释。
10. 只能输出JSON。
"""

    result = call_llm(prompt, temperature=0.0)
    return extract_json(result)