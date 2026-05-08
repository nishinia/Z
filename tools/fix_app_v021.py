from pathlib import Path

APP_PATH = Path("app.py")
BACKUP_PATH = Path("app_broken_backup.py")

text = APP_PATH.read_text(encoding="utf-8")

# 备份当前坏掉的 app.py
BACKUP_PATH.write_text(text, encoding="utf-8")

marker = "# ==================================================\n# V0.2 公司模板驱动版 - 气缸生成器"

if marker in text:
    prefix = text.split(marker)[0].rstrip()
else:
    prefix = text.rstrip()

suffix = r'''
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
'''

APP_PATH.write_text(prefix + "\n\n" + suffix, encoding="utf-8")

print("app.py 已修复。原坏文件已备份为 app_broken_backup.py")