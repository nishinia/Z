from pathlib import Path

APP_PATH = Path("app.py")
BACKUP_PATH = Path("app_backup_before_v051_warning_fix.py")

text = APP_PATH.read_text(encoding="utf-8")
BACKUP_PATH.write_text(text, encoding="utf-8")

marker = "# ==================================================\n# V0.5.1 整机中文需求 → AI解析 → 人工确认 → 完整工程包"

if marker in text:
    prefix = text.split(marker)[0].rstrip()
else:
    prefix = text.rstrip()

v051_block = r'''
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

# 初始化编辑框内容：只在不存在时初始化，避免 value + session_state 冲突
if "v051_project_info_editor" not in st.session_state:
    st.session_state["v051_project_info_editor"] = """{
    "project_name": "AI_Device_Project_V051",
    "plc": "Omron NJ501",
    "description": "等待AI解析或人工填写。"
}"""

if "v051_cylinder_config_editor" not in st.session_state:
    st.session_state["v051_cylinder_config_editor"] = """{
    "cylinders": []
}"""

if "v051_station_config_editor" not in st.session_state:
    st.session_state["v051_station_config_editor"] = """{
    "program_name": "S1_Auto_Generated",
    "station_name": "S1_自动工站",
    "station_num": 1,
    "steps": []
}"""

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
        "v051_project_info_editor",
        "v051_cylinder_config_editor",
        "v051_station_config_editor",
        "v051_device_config_full_text"
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

        # 只写入 widget 对应 key；text_area 不再传 value，避免 Streamlit 警告
        st.session_state["v051_project_info_editor"] = project_info_json_v051
        st.session_state["v051_cylinder_config_editor"] = cylinder_config_json_v051
        st.session_state["v051_station_config_editor"] = station_config_json_v051
        st.session_state["v051_device_config_full_text"] = full_device_config_json_v051

        st.success("AI解析完成，请检查并修改下面的 JSON，然后再生成工程包。")
        st.rerun()

    except Exception as e:
        st.error(f"AI解析失败：{e}")


st.subheader("② 人工确认 / 修改 AI 解析结果")

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
'''

APP_PATH.write_text(prefix + "\n\n" + v051_block, encoding="utf-8")

print("app.py 已修复 V0.5.1 Streamlit session_state 警告。")
print("原文件已备份为 app_backup_before_v051_warning_fix.py")