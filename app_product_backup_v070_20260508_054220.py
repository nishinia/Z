import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

import streamlit as st

from company_generators.multi_station_ai_parser import parse_multi_station_requirement
from company_generators.multi_station_project_generator import generate_multi_station_project_package


PRODUCT_VERSION = "V0.6.5"
CORE_VERSION = "V0.6.4"
PROJECT_DIR = Path(r"D:\AI\plc_ai_system")
OUTPUT_DIR = PROJECT_DIR / "output"
MAIN_ZIP = OUTPUT_DIR / "AI_Device_Project_Package_V06.zip"
FINAL_ZIP = OUTPUT_DIR / "AI_Device_Project_Package_V065_Final.zip"


REQUIRED_FINAL_FILES = [
    "00_README.txt",
    "validation_report.txt",
    "manifest.json",
    "00_DUT_Struct_Generated.st",
    "00_Global_Variables_Generated.st",
    "01_Cylinder_Action_Generated.st",
    "02_Station_S1_Auto_Generated.st",
    "03_Station_S2_Auto_Generated.st",
    "04_Machine_Auto_Main_Generated.st",
    "HMI_Variable_List.csv",
    "IO_Mapping_List.csv",
    "IO_Mapping_Enhanced.csv",
    "Alarm_List.csv",
    "Step_List.csv",
    "Variable_CrossReference_Report.txt",
    "Final_Acceptance_Report.txt",
    "Sysmac_Import_Guide.txt",
    "ST_Quality_Report.txt",
    "configs/cylinder_config.json",
    "configs/station_configs.json",
    "configs/v062_station_chain.json",
    "configs/company_symbols.json",
    "template_source/FB_Cylinder.st",
]


DEFAULT_REQUIREMENT = """项目名称：AI_Device_Project_V065_Final。
PLC使用欧姆龙NJ501。

设备有两个气缸：
CY1 上料夹爪气缸，原点 I1_0，动点 I1_1，原点阀 Q1_0，动点阀 Q1_1。
CY2 NG剔除气缸，原点 I2_0，动点 I2_1，原点阀 Q2_0，动点阀 Q2_1。

S1上料工站，工站号1。
流程：等待启动后，CY1上料夹爪气缸到动点；CY1动点到位后，CY1回原点；CY1原点到位后流程完成。
每个动作步骤超时3000ms，报警编号按步骤号设置。

S2分拣工站，工站号2。
流程：等待S1完成后，CY2 NG剔除气缸到动点；CY2动点到位后，CY2回原点；CY2原点到位后流程完成。
每个动作步骤超时3000ms，报警编号按步骤号设置。

任意气缸动作超时需要报警；
按复位按钮后清除报警并回到初始状态。
"""


def read_text(path: Path):
    for enc in ["utf-8", "utf-8-sig", "gbk"]:
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(encoding="utf-8", errors="ignore")


def zip_contains(zip_path: Path, suffix: str):
    if not zip_path.exists():
        return False

    with zipfile.ZipFile(zip_path, "r") as z:
        names = [n.replace("\\", "/") for n in z.namelist()]
        return any(n.endswith(suffix) for n in names)


def validate_zip(zip_path: Path):
    result = []

    if not zip_path.exists():
        return False, [("ZIP文件不存在", False)]

    with zipfile.ZipFile(zip_path, "r") as z:
        names = [n.replace("\\", "/") for n in z.namelist()]

    ok = True

    for item in REQUIRED_FINAL_FILES:
        hit = any(n.endswith(item) for n in names)
        result.append((item, hit))
        if not hit:
            ok = False

    return ok, result


def get_config_summary(config: dict):
    project_info = config.get("project_info", {})
    cylinder_config = config.get("cylinder_config", {})
    station_configs = config.get("station_configs", [])

    cylinders = cylinder_config.get("cylinders", [])

    return {
        "project_name": project_info.get("project_name", ""),
        "plc": project_info.get("plc", ""),
        "cylinder_count": len(cylinders),
        "station_count": len(station_configs),
        "station_names": [
            s.get("station_name") or s.get("program_name") or s.get("station_id", "")
            for s in station_configs
            if isinstance(s, dict)
        ],
    }


st.set_page_config(
    page_title="PLC数字工程师 V0.6.5",
    page_icon="🏭",
    layout="wide",
)

st.title("🏭 PLC数字工程师成品版操作台")
st.caption(f"Product Console {PRODUCT_VERSION} ｜ Core Generator {CORE_VERSION}")

with st.sidebar:
    st.header("当前版本")
    st.write(f"成品操作台：**{PRODUCT_VERSION}**")
    st.write(f"工程生成核心：**{CORE_VERSION}**")
    st.divider()
    st.write("当前主流程：")
    st.write("1. 输入整机中文需求")
    st.write("2. AI解析多工站")
    st.write("3. 人工确认")
    st.write("4. 一键生成最终ZIP")
    st.write("5. 下载交付包")
    st.divider()
    st.warning("正式上机前必须完成 Sysmac Studio 编译、仿真、IO点检和安全验证。")

st.success("这是整理后的成品版页面。旧版测试模块不在这里显示。")

if "v065_config" not in st.session_state:
    st.session_state["v065_config"] = None

if "v065_result" not in st.session_state:
    st.session_state["v065_result"] = None

if "v065_confirmed" not in st.session_state:
    st.session_state["v065_confirmed"] = False


st.header("1️⃣ 输入整机中文需求")

requirement_text = st.text_area(
    "把设备需求、气缸、工站、流程、报警、复位要求写在这里：",
    value=DEFAULT_REQUIREMENT,
    height=360,
    key="v065_requirement_text",
)

col_parse, col_clear = st.columns([1, 1])

with col_parse:
    parse_clicked = st.button(
        "🤖 第一步：AI解析整机需求",
        use_container_width=True,
        type="primary",
    )

with col_clear:
    if st.button("清空当前解析结果", use_container_width=True):
        st.session_state["v065_config"] = None
        st.session_state["v065_result"] = None
        st.session_state["v065_confirmed"] = False
        st.rerun()


if parse_clicked:
    try:
        with st.spinner("AI正在解析整机中文需求，请稍等..."):
            parsed_config = parse_multi_station_requirement(requirement_text)

        st.session_state["v065_config"] = parsed_config
        st.session_state["v065_result"] = None
        st.session_state["v065_confirmed"] = False
        st.success("AI解析完成，请继续人工确认。")

    except Exception as e:
        st.error(f"AI解析失败：{e}")


config = st.session_state.get("v065_config")

if config:
    st.header("2️⃣ 人工确认 AI 解析结果")

    summary = get_config_summary(config)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("项目名称", summary["project_name"] or "未识别")
    c2.metric("PLC", summary["plc"] or "未识别")
    c3.metric("气缸数量", summary["cylinder_count"])
    c4.metric("工站数量", summary["station_count"])

    tab_project, tab_cylinder, tab_station, tab_json = st.tabs([
        "Project Info",
        "Cylinder Config",
        "Station Configs",
        "完整JSON",
    ])

    with tab_project:
        st.code(
            json.dumps(config.get("project_info", {}), ensure_ascii=False, indent=4),
            language="json",
        )

    with tab_cylinder:
        st.code(
            json.dumps(config.get("cylinder_config", {}), ensure_ascii=False, indent=4),
            language="json",
        )

    with tab_station:
        st.code(
            json.dumps(config.get("station_configs", []), ensure_ascii=False, indent=4),
            language="json",
        )

    with tab_json:
        st.code(
            json.dumps(config, ensure_ascii=False, indent=4),
            language="json",
        )

    st.session_state["v065_confirmed"] = st.checkbox(
        "我已人工确认：工站、气缸、流程、报警、复位逻辑基本正确",
        value=st.session_state.get("v065_confirmed", False),
    )

    st.header("3️⃣ 一键生成最终工程包")

    generate_disabled = not st.session_state["v065_confirmed"]

    if generate_disabled:
        st.info("请先勾选人工确认，再生成最终工程包。")

    if st.button(
        "📦 第二步：生成 V0.6.5 最终工程包 ZIP",
        use_container_width=True,
        type="primary",
        disabled=generate_disabled,
    ):
        try:
            project_info = config.get("project_info", {})
            cylinder_config = config.get("cylinder_config", {})
            station_configs = config.get("station_configs", [])

            with st.spinner("正在生成最终工程包 ZIP..."):
                result = generate_multi_station_project_package(
                    project_info=project_info,
                    cylinder_config=cylinder_config,
                    station_configs=station_configs,
                )

            st.session_state["v065_result"] = result

            if not result.get("ok"):
                st.error("最终工程包生成失败。")
                for err in result.get("errors", []):
                    st.warning(err)
            else:
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

                confirmed_json_path = OUTPUT_DIR / "product_console_confirmed_config_v065.json"
                confirmed_json_path.write_text(
                    json.dumps(config, ensure_ascii=False, indent=4),
                    encoding="utf-8",
                )

                zip_path = Path(result["zip_path"])

                if zip_path.exists():
                    shutil.copy2(zip_path, FINAL_ZIP)

                st.success("V0.6.5 最终工程包生成完成。")

        except Exception as e:
            st.error(f"最终工程包生成异常：{e}")


result = st.session_state.get("v065_result")

if result and result.get("ok"):
    st.header("4️⃣ 下载最终交付包")

    zip_path = FINAL_ZIP if FINAL_ZIP.exists() else Path(result["zip_path"])

    ok, check_items = validate_zip(zip_path)

    if ok:
        st.success("最终 ZIP 静态验收通过。")
    else:
        st.error("最终 ZIP 存在缺失文件，请检查下方清单。")

    with st.expander("查看最终ZIP文件检查清单", expanded=False):
        for name, hit in check_items:
            if hit:
                st.write(f"✅ {name}")
            else:
                st.write(f"❌ {name}")

    if zip_path.exists():
        st.download_button(
            label="⬇️ 下载 V0.6.5 最终工程包 ZIP",
            data=zip_path.read_bytes(),
            file_name="AI_Device_Project_Package_V065_Final.zip",
            mime="application/zip",
            use_container_width=True,
        )

        st.write("工程包路径：")
        st.code(str(zip_path))

    package_dir = Path(result["package_dir"])

    st.subheader("核心交付文件预览")

    preview_files = [
        "Final_Acceptance_Report.txt",
        "ST_Quality_Report.txt",
        "Sysmac_Import_Guide.txt",
        "validation_report.txt",
    ]

    for filename in preview_files:
        p = package_dir / filename
        if p.exists():
            with st.expander(filename, expanded=False):
                st.text(read_text(p))

    st.subheader("生成文件列表")
    for f in result.get("files", []):
        st.write(f)

else:
    st.header("4️⃣ 下载最终交付包")
    st.info("生成成功后，这里会出现下载按钮。")
