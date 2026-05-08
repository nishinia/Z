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
            else:
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
# ==================================================
# V0.3 公司模板驱动版 - 工站 Station 生成器
# ==================================================
from company_generators.station_generator import (
    render_station_program,
    validate_station_config
)

st.divider()

st.header("🏗️ V0.3 公司模板驱动版 - 工站 Station 生成器")

st.info(
    "这一模块根据公司 Station[_StationNum].nAutoStep 风格生成工站流程，不让AI自由写ST。"
)

default_station_json = """{
    "program_name": "S1_Auto_Generated",
    "station_name": "S1_测试工站",
    "station_num": 1,
    "run_condition": "Machine_Data.IN.bEStop AND Machine_Data.IN.bSafety AND Machine_Data.IN.bAirOn",
    "reset_condition": "Machine_Data.bReset",
    "start_condition": "bRunAble AND Station[_StationNum].bRunning",
    "steps": [
        {
            "step": 0,
            "title": "INIT 初始化",
            "actions": [
                "Cylinder_Data.CY1.Input.bAuto:=FALSE",
                "Cylinder_Data.CY2.Input.bAuto:=FALSE"
            ],
            "next_condition": "bRunAble",
            "next_step": 10
        },
        {
            "step": 10,
            "title": "等待启动",
            "actions": [],
            "next_condition": "bRunAble AND Station[_StationNum].bRunning",
            "next_step": 20
        },
        {
            "step": 20,
            "title": "CY1拨料上下气缸到动点",
            "actions": [
                "Cylinder_Data.CY1.Input.bAuto:=TRUE"
            ],
            "next_condition": "Cylinder_Data.CY1.Output.bWP_Delay",
            "next_step": 30
        },
        {
            "step": 30,
            "title": "CY2 NG剔除气缸到动点",
            "actions": [
                "Cylinder_Data.CY2.Input.bAuto:=TRUE"
            ],
            "next_condition": "Cylinder_Data.CY2.Output.bWP_Delay",
            "next_step": 40
        },
        {
            "step": 40,
            "title": "CY2 NG剔除气缸回原点",
            "actions": [
                "Cylinder_Data.CY2.Input.bAuto:=FALSE"
            ],
            "next_condition": "Cylinder_Data.CY2.Output.bHP_Delay",
            "next_step": 50
        },
        {
            "step": 50,
            "title": "CY1拨料上下气缸回原点",
            "actions": [
                "Cylinder_Data.CY1.Input.bAuto:=FALSE"
            ],
            "next_condition": "Cylinder_Data.CY1.Output.bHP_Delay",
            "next_step": 0
        },
        {
            "step": 999,
            "title": "ERROR 报警停机",
            "actions": [
                "Cylinder_Data.CY1.Input.bAuto:=FALSE",
                "Cylinder_Data.CY2.Input.bAuto:=FALSE",
                "Station[_StationNum].bRunning:=FALSE"
            ],
            "next_condition": "Machine_Data.bReset",
            "next_step": 0
        }
    ]
}"""

station_json_text = st.text_area(
    "工站配置 JSON：",
    value=default_station_json,
    height=520,
    key="station_json_text"
)

if st.button("🏗️ 生成公司模板 Station 程序", use_container_width=True):
    try:
        station_config = json.loads(station_json_text)

        station_errors = validate_station_config(station_config)

        if station_errors:
            st.error("工站配置存在问题：")
            for err in station_errors:
                st.warning(err)
        else:
            station_code = render_station_program(station_config)

            output_dir = Path("output")
            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / "Station_Generated.st"
            output_file.write_text(station_code, encoding="utf-8")

            st.success("Station 工站程序已生成。")

            st.code(station_code, language="pascal")

            st.download_button(
                label="下载 Station_Generated.st",
                data=station_code,
                file_name="Station_Generated.st",
                mime="text/plain"
            )

    except json.JSONDecodeError as e:
        st.error(f"JSON格式错误：{e}")

    except Exception as e:
        st.error(f"生成失败：{e}")
# ==================================================
# V0.3.1 公司模板驱动版 - AI中文工艺转Station JSON
# ==================================================
from company_generators.station_ai_parser import parse_station_requirement

st.divider()

st.header("🧠 V0.3.1 AI解析工站工艺 → 公司模板Station程序")

st.info(
    "这里让AI只负责把中文工艺转成Station JSON，真正的ST仍然由公司Station模板生成。"
)

default_station_requirement = """S1工站，工站号1。
流程：等待启动后，CY1拨料上下气缸先到动点，CY1动点到位后，CY2 NG剔除气缸到动点。
CY2动点到位后，CY2回原点。CY2原点到位后，CY1回原点。
CY1原点到位后流程完成，回到等待启动。"""

station_requirement = st.text_area(
    "请输入工站中文工艺：",
    value=default_station_requirement,
    height=220,
    key="station_requirement_text"
)

if st.button("🧠 AI解析并生成公司模板Station程序", use_container_width=True):
    try:
        with st.spinner("AI正在解析工站工艺..."):
            parsed_station_config = parse_station_requirement(station_requirement)

        station_errors = validate_station_config(parsed_station_config)

        if station_errors:
            st.error("AI解析出的工站配置存在问题：")
            for err in station_errors:
                st.warning(err)
        else:
            parsed_station_json_text = json.dumps(
                parsed_station_config,
                ensure_ascii=False,
                indent=4
            )

            st.subheader("AI解析出的 Station JSON")
            st.code(parsed_station_json_text, language="json")

            station_code = render_station_program(parsed_station_config)

            output_dir = Path("output")
            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / "Station_AI_Generated.st"
            output_file.write_text(station_code, encoding="utf-8")

            st.subheader("公司模板生成的 Station 程序")
            st.code(station_code, language="pascal")

            st.download_button(
                label="下载 Station_AI_Generated.st",
                data=station_code,
                file_name="Station_AI_Generated.st",
                mime="text/plain"
            )

            st.download_button(
                label="下载 AI解析Station JSON",
                data=parsed_station_json_text,
                file_name="station_config_ai.json",
                mime="application/json"
            )

    except Exception as e:
        st.error(f"AI解析或生成失败：{e}")
# ==================================================
# V0.4 公司模板驱动版 - 完整设备工程包生成器
# ==================================================
from company_generators.project_package_generator import generate_project_package

st.divider()

st.header("📦 V0.4 公司模板驱动版 - 完整设备工程包")

st.info(
    "这一模块会把气缸配置和工站配置合并，生成完整工程包 ZIP。"
)

default_project_info_json = """{
    "project_name": "AI_Device_Project_V04",
    "plc": "Omron NJ501",
    "description": "双气缸测试工站：CY1拨料上下气缸，CY2 NG剔除气缸，使用公司模板生成 Cylinder_Action 和 Station 程序。"
}"""

project_info_json_text = st.text_area(
    "项目信息 JSON：",
    value=default_project_info_json,
    height=160,
    key="project_info_json_text"
)

try:
    default_cylinder_config_text = Path("configs/sample_cylinders.json").read_text(encoding="utf-8")
except Exception:
    default_cylinder_config_text = """{
    "cylinders": []
}"""

try:
    default_station_config_text = Path("configs/sample_station.json").read_text(encoding="utf-8")
except Exception:
    default_station_config_text = """{
    "steps": []
}"""

package_cylinder_json_text = st.text_area(
    "工程包气缸配置 JSON：",
    value=default_cylinder_config_text,
    height=280,
    key="package_cylinder_json_text"
)

package_station_json_text = st.text_area(
    "工程包工站配置 JSON：",
    value=default_station_config_text,
    height=420,
    key="package_station_json_text"
)

if st.button("📦 生成完整设备工程包 ZIP", use_container_width=True):
    try:
        project_info = json.loads(project_info_json_text)
        cylinder_config = json.loads(package_cylinder_json_text)
        station_config = json.loads(package_station_json_text)

        result = generate_project_package(
            cylinder_config=cylinder_config,
            station_config=station_config,
            project_info=project_info
        )

        if not result["ok"]:
            st.error("工程包生成失败：")
            for err in result["errors"]:
                st.warning(err)
        else:
            st.success("完整设备工程包已生成。")

            st.subheader("生成文件列表")
            for f in result["files"]:
                st.write(f)

            zip_path = Path(result["zip_path"])
            zip_bytes = zip_path.read_bytes()

            st.download_button(
                label="下载 AI_Device_Project_Package.zip",
                data=zip_bytes,
                file_name="AI_Device_Project_Package.zip",
                mime="application/zip"
            )

    except json.JSONDecodeError as e:
        st.error(f"JSON格式错误：{e}")

    except Exception as e:
        st.error(f"生成失败：{e}")
# ==================================================
# V0.5 整机中文需求 → 完整设备工程包
# ==================================================
from company_generators.device_ai_parser import parse_device_requirement

st.divider()

st.header("🤖 V0.5 整机中文需求 → 完整设备工程包")

st.info(
    "这一模块会让AI把整机中文需求解析成 cylinder_config 和 station_config，然后用公司模板生成完整工程包 ZIP。"
)

default_device_requirement = """项目名称：AI_Device_Project_V05。
PLC使用欧姆龙NJ501。

设备有两个气缸：
CY1 拨料上下气缸，原点 I1_0 AND I1_3，动点 I1_1 AND I1_4，原点阀 Q1_7，动点阀 Q1_6。
CY2 NG剔除气缸，原点 I2_0，动点 I2_1，原点阀 Q2_0，动点阀 Q2_1。

S1工站，工站号1。
流程：等待启动后，CY1拨料上下气缸先到动点；CY1动点到位后，CY2 NG剔除气缸到动点；
CY2动点到位后，CY2回原点；CY2原点到位后，CY1回原点；
CY1原点到位后流程完成，回到等待启动。
每个动作步骤超时3000ms，报警编号按步骤号设置。"""

device_requirement = st.text_area(
    "请输入整机中文需求：",
    value=default_device_requirement,
    height=360,
    key="device_requirement_text"
)

if st.button("🤖 AI解析整机需求并生成完整工程包", use_container_width=True):
    try:
        with st.spinner("AI正在解析整机需求，请等待..."):
            device_config = parse_device_requirement(device_requirement)

        project_info = device_config.get("project_info", {})
        cylinder_config = device_config.get("cylinder_config", {})
        station_config = device_config.get("station_config", {})

        st.subheader("AI解析出的 Project Info")
        st.code(json.dumps(project_info, ensure_ascii=False, indent=4), language="json")

        st.subheader("AI解析出的 Cylinder Config")
        st.code(json.dumps(cylinder_config, ensure_ascii=False, indent=4), language="json")

        st.subheader("AI解析出的 Station Config")
        st.code(json.dumps(station_config, ensure_ascii=False, indent=4), language="json")

        result = generate_project_package(
            cylinder_config=cylinder_config,
            station_config=station_config,
            project_info=project_info
        )

        if not result["ok"]:
            st.error("完整工程包生成失败：")
            for err in result["errors"]:
                st.warning(err)
        else:
            output_dir = Path("output")
            output_dir.mkdir(parents=True, exist_ok=True)

            full_config_path = output_dir / "device_config_ai.json"
            full_config_text = json.dumps(device_config, ensure_ascii=False, indent=4)
            full_config_path.write_text(full_config_text, encoding="utf-8")

            st.success("V0.5 完整设备工程包已生成。")

            st.subheader("工程包文件列表")
            for f in result["files"]:
                st.write(f)

            zip_path = Path(result["zip_path"])
            zip_bytes = zip_path.read_bytes()

            st.download_button(
                label="下载 V0.5 AI_Device_Project_Package.zip",
                data=zip_bytes,
                file_name="AI_Device_Project_Package_V05.zip",
                mime="application/zip"
            )

            st.download_button(
                label="下载 AI解析整机JSON",
                data=full_config_text,
                file_name="device_config_ai.json",
                mime="application/json"
            )

    except Exception as e:
        st.error(f"V0.5 生成失败：{e}")


# ==================================================
# V0.5.1 整机中文需求 → AI解析 → 人工确认 → 完整工程包
# ==================================================
import json
from pathlib import Path

from company_generators.device_ai_parser import parse_device_requirement
from company_generators.project_package_generator import generate_project_package

st.divider()

st.header("🧩 V0.5.1 整机需求 → AI解析 → 人工确认 → 工程包")

st.info(
    "这一模块先让AI解析整机需求，然后把解析结果显示出来。工程师确认或修改 JSON 后，再生成完整工程包。"
)

default_device_requirement_v051 = """项目名称：AI_Device_Project_V051。
PLC使用欧姆龙NJ501。

设备有两个气缸：
CY1 拨料上下气缸，原点 I1_0 AND I1_3，动点 I1_1 AND I1_4，原点阀 Q1_7，动点阀 Q1_6。
CY2 NG剔除气缸，原点 I2_0，动点 I2_1，原点阀 Q2_0，动点阀 Q2_1。

S1工站，工站号1。
流程：等待启动后，CY1拨料上下气缸先到动点；
CY1动点到位后，CY2 NG剔除气缸到动点；
CY2动点到位后，CY2回原点；
CY2原点到位后，CY1回原点；
CY1原点到位后流程完成，回到等待启动。
每个动作步骤超时3000ms，报警编号按步骤号设置。"""

device_requirement_v051 = st.text_area(
    "请输入整机中文需求：",
    value=default_device_requirement_v051,
    height=320,
    key="v051_device_requirement_text"
)

col_parse_v051, col_clear_v051 = st.columns([1, 1])

with col_parse_v051:
    parse_btn_v051 = st.button(
        "① AI解析整机需求",
        use_container_width=True,
        key="v051_parse_device_btn"
    )

with col_clear_v051:
    clear_btn_v051 = st.button(
        "清空 V0.5.1 解析结果",
        use_container_width=True,
        key="v051_clear_btn"
    )

if clear_btn_v051:
    for k in [
        "v051_project_info_text",
        "v051_cylinder_config_text",
        "v051_station_config_text",
        "v051_device_config_full_text",
        "v051_project_info_editor",
        "v051_cylinder_config_editor",
        "v051_station_config_editor"
    ]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

if parse_btn_v051:
    try:
        with st.spinner("AI正在解析整机需求，请等待..."):
            device_config_v051 = parse_device_requirement(device_requirement_v051)

        project_info_v051 = device_config_v051.get("project_info", {})
        cylinder_config_v051 = device_config_v051.get("cylinder_config", {})
        station_config_v051 = device_config_v051.get("station_config", {})

        project_info_json_v051 = json.dumps(
            project_info_v051,
            ensure_ascii=False,
            indent=4
        )

        cylinder_config_json_v051 = json.dumps(
            cylinder_config_v051,
            ensure_ascii=False,
            indent=4
        )

        station_config_json_v051 = json.dumps(
            station_config_v051,
            ensure_ascii=False,
            indent=4
        )

        full_device_config_json_v051 = json.dumps(
            device_config_v051,
            ensure_ascii=False,
            indent=4
        )

        # 关键修复：
        # 同时写入 text 缓存和真正 text_area 使用的 editor key
        st.session_state["v051_project_info_text"] = project_info_json_v051
        st.session_state["v051_cylinder_config_text"] = cylinder_config_json_v051
        st.session_state["v051_station_config_text"] = station_config_json_v051
        st.session_state["v051_device_config_full_text"] = full_device_config_json_v051

        st.session_state["v051_project_info_editor"] = project_info_json_v051
        st.session_state["v051_cylinder_config_editor"] = cylinder_config_json_v051
        st.session_state["v051_station_config_editor"] = station_config_json_v051

        st.success("AI解析完成，请检查并修改下面的 JSON，然后再生成工程包。")
        st.rerun()

    except Exception as e:
        st.error(f"AI解析失败：{e}")


st.subheader("② 人工确认 / 修改 AI 解析结果")

default_project_info_v051 = st.session_state.get(
    "v051_project_info_text",
    """{
    "project_name": "AI_Device_Project_V051",
    "plc": "Omron NJ501",
    "description": "等待AI解析或人工填写。"
}"""
)

default_cylinder_config_v051 = st.session_state.get(
    "v051_cylinder_config_text",
    """{
    "cylinders": []
}"""
)

default_station_config_v051 = st.session_state.get(
    "v051_station_config_text",
    """{
    "program_name": "S1_Auto_Generated",
    "station_name": "S1_自动工站",
    "station_num": 1,
    "steps": []
}"""
)

project_info_text_v051 = st.text_area(
    "Project Info JSON：",
    height=160,
    key="v051_project_info_editor"
)

cylinder_config_text_v051 = st.text_area(
    "Cylinder Config JSON：",
    height=300,
    key="v051_cylinder_config_editor"
)

station_config_text_v051 = st.text_area(
    "Station Config JSON：",
    height=480,
    key="v051_station_config_editor"
)

generate_confirmed_btn_v051 = st.button(
    "② 确认无误，生成完整工程包 ZIP",
    use_container_width=True,
    key="v051_generate_confirmed_package_btn"
)

if generate_confirmed_btn_v051:
    try:
        project_info_v051 = json.loads(project_info_text_v051)
        cylinder_config_v051 = json.loads(cylinder_config_text_v051)
        station_config_v051 = json.loads(station_config_text_v051)

        with st.spinner("正在根据确认后的 JSON 生成完整工程包..."):
            result_v051 = generate_project_package(
                cylinder_config=cylinder_config_v051,
                station_config=station_config_v051,
                project_info=project_info_v051
            )

        if not result_v051["ok"]:
            st.error("工程包生成失败：")
            for err in result_v051["errors"]:
                st.warning(err)
        else:
            output_dir = Path("output")
            output_dir.mkdir(parents=True, exist_ok=True)

            confirmed_device_config = {
                "project_info": project_info_v051,
                "cylinder_config": cylinder_config_v051,
                "station_config": station_config_v051
            }

            confirmed_config_text = json.dumps(
                confirmed_device_config,
                ensure_ascii=False,
                indent=4
            )

            confirmed_config_path = output_dir / "device_config_confirmed_v051.json"
            confirmed_config_path.write_text(confirmed_config_text, encoding="utf-8")

            st.success("V0.5.1 工程包生成完成。")

            st.subheader("工程包文件列表")
            for f in result_v051["files"]:
                st.write(f)

            zip_path_v051 = Path(result_v051["zip_path"])
            zip_bytes_v051 = zip_path_v051.read_bytes()

            st.download_button(
                label="下载 V0.5.1 AI_Device_Project_Package.zip",
                data=zip_bytes_v051,
                file_name="AI_Device_Project_Package_V051.zip",
                mime="application/zip"
            )

            st.download_button(
                label="下载人工确认后的整机JSON",
                data=confirmed_config_text,
                file_name="device_config_confirmed_v051.json",
                mime="application/json"
            )

            validation_path = Path(result_v051["package_dir"]) / "validation_report.txt"
            if validation_path.exists():
                st.subheader("validation_report.txt 预览")
                st.text(validation_path.read_text(encoding="utf-8"))

    except json.JSONDecodeError as e:
        st.error(f"JSON格式错误：{e}")

    except Exception as e:
        st.error(f"V0.5.1 工程包生成失败：{e}")
# ==================================================
# V0.6 多工站 / 多气缸 / 多流程工程包生成器
# ==================================================
from company_generators.multi_station_project_generator import (
    generate_multi_station_project_package
)

st.divider()

st.header("🏭 V0.6 多工站 / 多气缸 / 多流程工程包")

st.info(
    "这一模块支持一个工程包生成多个 Station 程序，例如 S1上料、S2扫码、S3分拣。"
)

try:
    default_multi_station_project_text = Path(
        "configs/sample_multi_station_project.json"
    ).read_text(encoding="utf-8")
except Exception:
    default_multi_station_project_text = """{
    "project_info": {
        "project_name": "AI_Device_Project_V06",
        "plc": "Omron NJ501",
        "description": "多工站工程包。"
    },
    "cylinder_config": {
        "cylinders": []
    },
    "station_configs": []
}"""

multi_station_project_text = st.text_area(
    "多工站工程配置 JSON：",
    value=default_multi_station_project_text,
    height=700,
    key="v06_multi_station_project_text"
)

if st.button("🏭 生成 V0.6 多工站完整工程包 ZIP", use_container_width=True):
    try:
        multi_config = json.loads(multi_station_project_text)

        project_info = multi_config.get("project_info", {})
        cylinder_config = multi_config.get("cylinder_config", {})
        station_configs = multi_config.get("station_configs", [])

        with st.spinner("正在生成 V0.6 多工站工程包..."):
            result_v06 = generate_multi_station_project_package(
                project_info=project_info,
                cylinder_config=cylinder_config,
                station_configs=station_configs
            )

        if not result_v06["ok"]:
            st.error("V0.6 多工站工程包生成失败：")
            for err in result_v06["errors"]:
                st.warning(err)
        else:
            st.success("V0.6 多工站工程包生成完成。")

            if result_v06.get("warnings"):
                st.subheader("警告")
                for warn in result_v06["warnings"]:
                    st.warning(warn)

            st.subheader("生成文件列表")
            for f in result_v06["files"]:
                st.write(f)

            st.subheader("工站程序文件")
            for f in result_v06["station_files"]:
                st.write(f)

            zip_path_v06 = Path(result_v06["zip_path"])
            zip_bytes_v06 = zip_path_v06.read_bytes()

            st.download_button(
                label="下载 V0.6 AI_Device_Project_Package_V06.zip",
                data=zip_bytes_v06,
                file_name="AI_Device_Project_Package_V06.zip",
                mime="application/zip"
            )

            validation_path_v06 = Path(result_v06["package_dir"]) / "validation_report.txt"
            if validation_path_v06.exists():
                st.subheader("validation_report.txt 预览")
                st.text(validation_path_v06.read_text(encoding="utf-8"))

    except json.JSONDecodeError as e:
        st.error(f"JSON格式错误：{e}")

    except Exception as e:
        st.error(f"V0.6 生成失败：{e}")

# ==================================================
# V0.6.1 整机中文需求 → AI解析多工站 → 多工站工程包
# ==================================================
from company_generators.multi_station_ai_parser import parse_multi_station_requirement
from company_generators.multi_station_project_generator import generate_multi_station_project_package

st.divider()

st.header("🤖 V0.6.2.2 整机中文需求 → AI解析多工站 → V0.6.2.1工程包")

st.info(
    "这一模块会把整机中文需求解析成多气缸、多工站配置，然后直接生成已集成整机主流程/HMI变量清单的 V0.6.2.1 工程包 ZIP。"
)

default_v061_requirement = """项目名称：AI_Device_Project_V061。
PLC使用欧姆龙NJ501。

设备有两个气缸：
CY1 上料夹爪气缸，原点 I1_0，动点 I1_1，原点阀 Q1_0，动点阀 Q1_1。
CY2 NG剔除气缸，原点 I2_0，动点 I2_1，原点阀 Q2_0，动点阀 Q2_1。

S1上料工站，工站号1。
流程：等待启动后，CY1上料夹爪气缸到动点；CY1动点到位后，CY1回原点；CY1原点到位后流程完成。
每个动作步骤超时3000ms，报警编号按步骤号设置。

S2分拣工站，工站号2。
流程：等待启动后，CY2 NG剔除气缸到动点；CY2动点到位后，CY2回原点；CY2原点到位后流程完成。
每个动作步骤超时3000ms，报警编号按步骤号设置。"""

v061_requirement = st.text_area(
    "请输入多工站整机中文需求：",
    value=default_v061_requirement,
    height=420,
    key="v061_requirement_text"
)

if st.button("🤖 AI解析并生成 V0.6.2.2 多工站整机工程包", use_container_width=True):
    try:
        with st.spinner("AI正在解析多工站整机需求..."):
            v061_config = parse_multi_station_requirement(v061_requirement)

        project_info = v061_config.get("project_info", {})
        cylinder_config = v061_config.get("cylinder_config", {})
        station_configs = v061_config.get("station_configs", [])

        st.subheader("AI解析出的 Project Info")
        st.code(json.dumps(project_info, ensure_ascii=False, indent=4), language="json")

        st.subheader("AI解析出的 Cylinder Config")
        st.code(json.dumps(cylinder_config, ensure_ascii=False, indent=4), language="json")

        st.subheader("AI解析出的 Station Configs")
        st.code(json.dumps(station_configs, ensure_ascii=False, indent=4), language="json")

        with st.spinner("正在生成 V0.6.2.2 多工站整机工程包..."):
            result_v061 = generate_multi_station_project_package(
                project_info=project_info,
                cylinder_config=cylinder_config,
                station_configs=station_configs
            )

        if not result_v061["ok"]:
            st.error("V0.6.2.2 多工站整机工程包生成失败：")
            for err in result_v061["errors"]:
                st.warning(err)
        else:
            output_dir = Path("output")
            output_dir.mkdir(parents=True, exist_ok=True)

            v061_config_text = json.dumps(v061_config, ensure_ascii=False, indent=4)
            v061_config_path = output_dir / "multi_station_config_ai_v0622.json"
            v061_config_path.write_text(v061_config_text, encoding="utf-8")

            st.success("V0.6.2.2 多工站整机工程包生成完成。")

            if result_v061.get("warnings"):
                st.subheader("警告")
                for warn in result_v061["warnings"]:
                    st.warning(warn)

            st.subheader("生成文件列表")
            for f in result_v061["files"]:
                st.write(f)

            st.subheader("工站程序文件")
            for f in result_v061["station_files"]:
                st.write(f)

            zip_path_v061 = Path(result_v061["zip_path"])
            zip_bytes_v061 = zip_path_v061.read_bytes()

            st.download_button(
                label="下载 V0.6.1 多工站工程包 ZIP",
                data=zip_bytes_v061,
                file_name="AI_Device_Project_Package_V0622.zip",
                mime="application/zip"
            )

            st.download_button(
                label="下载 AI解析多工站JSON",
                data=v061_config_text,
                file_name="multi_station_config_ai_v0622.json",
                mime="application/json"
            )

            validation_path_v061 = Path(result_v061["package_dir"]) / "validation_report.txt"
            if validation_path_v061.exists():
                st.subheader("validation_report.txt 预览")
                st.text(validation_path_v061.read_text(encoding="utf-8"))

    except Exception as e:
        st.error(f"V0.6.1 生成失败：{e}")