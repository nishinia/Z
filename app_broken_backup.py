import io
import zipfile
import streamlit as st

from generator import generate_project, build_st_file, build_project_json
from validator import validate_code


st.set_page_config(
    page_title="PLC数字工程师 NJ501",
    layout="wide"
)

st.title("🤖 工业级 PLC 数字工程师 - NJ501版")

st.warning(
    "注意：AI生成的PLC代码只能作为工程模板，必须由工程师审核、仿真、现场验证后才能用于真实设备。"
)

desc = st.text_area(
    "请输入产线/设备需求：",
    height=220,
    placeholder="例如：双工位上料，产品到位后触发基恩士扫码，OK走主线，NG气缸剔除。要求包含急停、门禁、气压低、扫码超时、满料报警。PLC使用欧姆龙NJ501，程序使用CASE状态机。"
)

col1, col2 = st.columns([1, 1])

with col1:
    generate_btn = st.button("🚀 生成工业PLC工程", use_container_width=True)

with col2:
    clear_btn = st.button("清空", use_container_width=True)

if clear_btn:
    st.session_state.clear()
    st.rerun()

if generate_btn:
    if not desc.strip():
        st.error("请先输入产线需求。")
    else:
        with st.spinner("AI工程师正在生成 IO、状态机、报警、FB、主程序，请等待..."):
            project = generate_project(desc)
            st_code = build_st_file(project)
            project_json = build_project_json(project)
            warnings = validate_code(st_code)

            st.session_state["project"] = project
            st.session_state["st_code"] = st_code
            st.session_state["project_json"] = project_json
            st.session_state["warnings"] = warnings

if "st_code" in st.session_state:
    st.success("生成完成。")

    warnings = st.session_state["warnings"]

    if warnings:
        st.subheader("⚠️ 自动校验提醒")
        for w in warnings:
            st.warning(w)
    else:
        st.info("基础结构校验通过。仍然需要人工审核。")

    tabs = st.tabs([
        "完整ST代码",
        "工程JSON",
        "下载工程包",
        "使用说明"
    ])

    with tabs[0]:
        st.code(st.session_state["st_code"], language="pascal")

        st.download_button(
            label="下载 plc_program.st",
            data=st.session_state["st_code"],
            file_name="plc_program.st",
            mime="text/plain"
        )

    with tabs[1]:
        st.code(st.session_state["project_json"], language="json")

        st.download_button(
            label="下载 project.json",
            data=st.session_state["project_json"],
            file_name="project.json",
            mime="application/json"
        )

    with tabs[2]:
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("plc_program.st", st.session_state["st_code"])
            zip_file.writestr("project.json", st.session_state["project_json"])
            zip_file.writestr("README.txt", """
PLC数字工程师生成工程包

文件说明：
1. plc_program.st    PLC ST代码模板
2. project.json      工程结构数据
3. README.txt        使用说明

注意：
AI生成内容必须经过工程师审核。
严禁未经验证直接下载到真实PLC控制设备。
""")

        st.download_button(
            label="📦 下载完整工程ZIP",
            data=zip_buffer.getvalue(),
            file_name="AI_NJ501_Project.zip",
            mime="application/zip"
        )

    with tabs[3]:
        st.markdown("""
### 使用流程

1. 输入设备/产线需求。
2. 点击生成。
3. 下载 ST 代码。
4. 在 Sysmac Studio 中手动建立 POU。
5. 将对应代码复制到 ST 程序中。
6. 根据现场 IO 地址修改变量映射。
7. 离线编译。
8. 仿真。
9. 空载测试。
10. 人工确认后再联机调试。

### 安全要求

- 急停必须走硬件安全回路。
- 安全门、光栅、气压、伺服报警必须独立校验。
- AI生成代码不能直接作为最终控制程序。
""")
# ==================================================
# V0.2 公司模板驱动版 - 气缸生成器
# ==================================================
import json
from pathlib import Path

from company_generators.cylinder_generator import (
    render_cylinder_action,
    validate_all_cylinders
)

st.divider()

st.header("🏭 V0.2 公司模板驱动版 - 气缸动作生成器")

st.info(
    "这一模块不会让AI自由写ST，而是根据公司模板格式生成 Cylinder_Action 程序。"
)

default_cylinder_json = """{
    "cylinders": [
        {
            "instance": "CY1",
            "data": "Cylinder_Data.CY1",
            "desc": "拨料上下气缸",
            "hp_sensor": "I1_0 AND I1_3",
            "wp_sensor": "I1_1 AND I1_4",
            "hp_valve": "Q1_7",
            "wp_valve": "Q1_6",
            "on_ilc": "TRUE",
            "off_ilc": "TRUE"
        },
        {
            "instance": "CY2",
            "data": "Cylinder_Data.CY2",
            "desc": "NG剔除气缸",
            "hp_sensor": "I2_0",
            "wp_sensor": "I2_1",
            "hp_valve": "Q2_0",
            "wp_valve": "Q2_1",
            "on_ilc": "TRUE",
            "off_ilc": "TRUE"
        }
    ]
}"""

cylinder_json_text = st.text_area(
    "气缸配置 JSON：",
    value=default_cylinder_json,
    height=360,
    key="cylinder_json_text"
)

if st.button("⚙️ 生成公司模板 Cylinder_Action", use_container_width=True):
    try:
        cylinder_config = json.loads(cylinder_json_text)
        cylinders = cylinder_config.get("cylinders", [])

if not cylinders:
    st.error("没有检测到 cylinders 配置。")
else:
    all_errors = validate_all_cylinders(cylinders)

    if all_errors:
        st.error("配置存在问题：")
        for err in all_errors:
            st.warning(err)
    else:
        cylinder_code = render_cylinder_action(cylinders)

        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "Cylinder_Action_Generated.st"
        output_file.write_text(cylinder_code, encoding="utf-8")

        st.success("Cylinder_Action 已生成。")

        st.code(cylinder_code, language="pascal")

        st.download_button(
            label="下载 Cylinder_Action_Generated.st",
            data=cylinder_code,
            file_name="Cylinder_Action_Generated.st",
            mime="text/plain"
        )

    except json.JSONDecodeError as e:
        st.error(f"JSON格式错误：{e}")

    except Exception as e:
        st.error(f"生成失败：{e}")
# ==================================================
# V0.2 公司模板驱动版 - AI中文需求转气缸JSON
# ==================================================
from company_generators.cylinder_ai_parser import parse_cylinder_requirement

st.divider()

st.header("🧠 AI解析气缸需求 → 公司模板JSON")

st.info(
    "这里让AI只负责把中文需求转成JSON，不允许AI直接写ST。真正的ST仍然由公司模板生成。"
)

default_cylinder_requirement = """CY1拨料上下气缸，原点 I1_0 AND I1_3，动点 I1_1 AND I1_4，原点阀 Q1_7，动点阀 Q1_6。
CY2 NG剔除气缸，原点 I2_0，动点 I2_1，原点阀 Q2_0，动点阀 Q2_1。"""

cylinder_requirement = st.text_area(
    "请输入气缸中文需求：",
    value=default_cylinder_requirement,
    height=180,
    key="cylinder_requirement_text"
)

if st.button("🧠 AI解析并生成公司模板气缸程序", use_container_width=True):
    try:
        with st.spinner("AI正在解析气缸需求..."):
            parsed_config = parse_cylinder_requirement(cylinder_requirement)

        cylinders = parsed_config.get("cylinders", [])

        if not cylinders:
            st.error("AI没有解析出 cylinders。")
        else:
all_errors = validate_all_cylinders(cylinders)

            if all_errors:
                st.error("AI解析结果存在问题：")
                for err in all_errors:
                    st.warning(err)

            st.subheader("AI解析出的气缸JSON")
            parsed_json_text = json.dumps(parsed_config, ensure_ascii=False, indent=4)
            st.code(parsed_json_text, language="json")

            cylinder_code = render_cylinder_action(cylinders)

            output_dir = Path("output")
            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / "Cylinder_Action_AI_Generated.st"
            output_file.write_text(cylinder_code, encoding="utf-8")

            st.subheader("公司模板生成的 Cylinder_Action")
            st.code(cylinder_code, language="pascal")

            st.download_button(
                label="下载 Cylinder_Action_AI_Generated.st",
                data=cylinder_code,
                file_name="Cylinder_Action_AI_Generated.st",
                mime="text/plain"
            )

            st.download_button(
                label="下载 AI解析JSON",
                data=parsed_json_text,
                file_name="cylinder_config_ai.json",
                mime="application/json"
            )

    except Exception as e:
        st.error(f"AI解析或生成失败：{e}")