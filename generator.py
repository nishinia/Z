import json
import re
from datetime import datetime

from llm import call_llm
from industrial_prompts import build_prompt
from fb_library import FB_LIBRARY


def clean_ai_output(text: str) -> str:
    """
    清理AI输出，去掉Markdown代码块等无效内容。
    """
    text = text.replace("```pascal", "")
    text = text.replace("```st", "")
    text = text.replace("```iecst", "")
    text = text.replace("```", "")
    return text.strip()


def generate_section(desc: str, section: str) -> str:
    prompt = build_prompt(desc, section)
    result = call_llm(prompt)
    return clean_ai_output(result)


def generate_project(desc: str) -> dict:
    io_def = generate_section(
        desc,
        "IO定义表，包含输入、输出、内部变量，使用标准命名。只输出变量表，不输出解释。"
    )

    state_machine = generate_section(
        desc,
        "主程序CASE状态机，包含INIT、IDLE、LOAD、SCAN、SORT、UNLOAD、ERROR。不要调用未定义函数。"
    )

    alarm_logic = generate_section(
        desc,
        "报警逻辑，包含报警代码、报警原因、复位条件。不要调用未定义函数。"
    )

    main_program = generate_section(
        desc,
        "主程序ST代码，只允许调用 FB_Conveyor、FB_Scanner、FB_Diverter、FB_AlarmManager。不要调用未定义函数。"
    )

    project = {
        "project_name": "AI_NJ501_Project",
        "plc": "Omron NJ501",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": desc,
        "sections": {
            "io_definition": io_def,
            "state_machine": state_machine,
            "alarm_logic": alarm_logic,
            "fb_library": FB_LIBRARY,
            "main_program": main_program
        }
    }

    return project


def build_st_file(project: dict) -> str:
    sections = project["sections"]

    return f"""
// ==================================================
// Project: {project["project_name"]}
// PLC: {project["plc"]}
// Created At: {project["created_at"]}
// ==================================================


// ==================================================
// 1. IO Definition
// ==================================================
{sections["io_definition"]}


// ==================================================
// 2. Function Block Library
// ==================================================
{sections["fb_library"]}


// ==================================================
// 3. Alarm Logic
// ==================================================
{sections["alarm_logic"]}


// ==================================================
// 4. State Machine
// ==================================================
{sections["state_machine"]}


// ==================================================
// 5. Main Program
// ==================================================
{sections["main_program"]}
"""


def build_project_json(project: dict) -> str:
    return json.dumps(project, ensure_ascii=False, indent=4)