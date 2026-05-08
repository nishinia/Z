from pathlib import Path
from datetime import datetime
import shutil
import zipfile
import py_compile
import textwrap

PROJECT_DIR = Path(r"D:\AI\plc_ai_system")
GEN_DIR = PROJECT_DIR / "company_generators"
OUTPUT_DIR = PROJECT_DIR / "output"

APP_PRODUCT = PROJECT_DIR / "app_product.py"
START_BAT = PROJECT_DIR / "start_plc_digital_engineer_v070.bat"
CHECK_SCRIPT = PROJECT_DIR / "check_v070_release.py"

PRODUCT_README = PROJECT_DIR / "README_PRODUCT_V070.md"
USER_MANUAL = PROJECT_DIR / "USER_MANUAL_V070.md"
RELEASE_NOTES = PROJECT_DIR / "RELEASE_NOTES_V070.md"

RELEASE_DIR = PROJECT_DIR / "release" / "PLC_Digital_Engineer_V070"
RELEASE_ZIP = PROJECT_DIR / "release" / "PLC_Digital_Engineer_V070_Release.zip"

BASE_PROJECT_ZIP = OUTPUT_DIR / "AI_Device_Project_Package_V06.zip"
FINAL_PRODUCT_ZIP = OUTPUT_DIR / "AI_Device_Project_Package_V070_Final.zip"


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")
    print("✅ 写入：", path)


def backup_file(path: Path):
    if path.exists():
        backup = path.with_name(
            f"{path.stem}_backup_v070_{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}"
        )
        shutil.copy2(path, backup)
        print("✅ 备份：", backup)


def patch_app_product():
    if not APP_PRODUCT.exists():
        print("❌ 找不到 app_product.py，请先确认 V0.6.5 已经完成。")
        return False

    backup_file(APP_PRODUCT)

    text = APP_PRODUCT.read_text(encoding="utf-8", errors="ignore")

    replacements = {
        'PRODUCT_VERSION = "V0.6.5"': 'PRODUCT_VERSION = "V0.7.0"',
        'PLC数字工程师成品版操作台': 'PLC数字工程师 V0.7.0 最终成品版',
        'V0.6.5 最终工程包 ZIP': 'V0.7.0 最终工程包 ZIP',
        'V0.6.5 最终交付包': 'V0.7.0 最终交付包',
        '下载 V0.6.5 最终工程包 ZIP': '下载 V0.7.0 最终工程包 ZIP',
        'AI_Device_Project_Package_V065_Final.zip': 'AI_Device_Project_Package_V070_Final.zip',
        'AI_Device_Project_Package_V065_Final': 'AI_Device_Project_Package_V070_Final',
        'V0.6.5': 'V0.7.0',
    }

    changed = 0
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            print("✅ 页面替换：", old, "→", new)
            changed += 1

    APP_PRODUCT.write_text(text, encoding="utf-8")

    try:
        py_compile.compile(str(APP_PRODUCT), doraise=True)
        print("✅ app_product.py 语法检查通过")
    except Exception as e:
        print("❌ app_product.py 语法错误：", e)
        return False

    print(f"✅ app_product.py 已升级到 V0.7.0，共替换 {changed} 项")
    return True


def generate_docs():
    write_text(PRODUCT_README, """
# PLC数字工程师 V0.7.0 最终成品版

## 产品定位

PLC数字工程师 V0.7.0 是一个面向欧姆龙 NJ/NX 系列 PLC 项目的工程包自动生成工具。

它可以从中文整机需求出发，经过 AI 解析、多工站配置确认，自动生成 PLC 工程交付包。

## 核心能力

- 整机中文需求输入
- AI 解析多气缸、多工站、多流程
- 人工确认解析结果
- 生成气缸动作 ST
- 生成多工站 ST
- 生成整机主流程 ST
- 生成 HMI 变量清单
- 生成 DUT 结构声明
- 生成全局变量声明
- 生成 IO 映射表
- 生成增强 IO 映射表
- 生成报警清单
- 生成步骤清单
- 生成变量交叉引用报告
- 生成 Sysmac Studio 导入说明
- 生成 ST 静态质量报告
- 生成最终验收报告
- 生成 manifest 追踪清单
- 生成 validation_report 校验报告
- 生成最终 ZIP 工程包

## 启动方式

在项目目录运行：

streamlit run app_product.py

或者双击：

start_plc_digital_engineer_v070.bat

## 重要说明

本工具生成的是 PLC 工程导入前文本包和辅助资料。

正式上机前必须由 PLC 工程师完成 Sysmac Studio 编译、变量确认、IO 绑定、仿真验证、单步调试、安全回路确认和现场联机测试。
""")

    write_text(USER_MANUAL, """
# 用户说明书 - PLC数字工程师 V0.7.0

## 一、启动软件

方法一：

cd /d D:\\AI\\plc_ai_system
streamlit run app_product.py

方法二：

双击：

start_plc_digital_engineer_v070.bat

## 二、操作流程

### 1. 输入整机中文需求

建议包含：

- 项目名称
- PLC 型号
- 气缸清单
- IO 点位
- 工站清单
- 每个工站流程
- 超时报警要求
- 复位要求
- 工站之间的顺序关系

### 2. 点击 AI 解析

点击页面中的：

🤖 第一步：AI解析整机需求

### 3. 人工确认

重点检查：

- 气缸数量是否正确
- 工站数量是否正确
- S1/S2/S3 顺序是否正确
- 每个工站步骤是否正确
- 报警和超时是否正确
- 复位要求是否被识别

### 4. 生成最终工程包

点击：

📦 第二步：生成 V0.7.0 最终工程包 ZIP

### 5. 下载 ZIP

点击：

⬇️ 下载 V0.7.0 最终工程包 ZIP

默认文件名：

AI_Device_Project_Package_V070_Final.zip

## 三、最终 ZIP 包内容

- 00_README.txt
- validation_report.txt
- manifest.json
- 00_DUT_Struct_Generated.st
- 00_Global_Variables_Generated.st
- 01_Cylinder_Action_Generated.st
- 02_Station_S1_Auto_Generated.st
- 03_Station_S2_Auto_Generated.st
- 04_Machine_Auto_Main_Generated.st
- HMI_Variable_List.csv
- IO_Mapping_List.csv
- IO_Mapping_Enhanced.csv
- Alarm_List.csv
- Step_List.csv
- Variable_CrossReference_Report.txt
- Final_Acceptance_Report.txt
- Sysmac_Import_Guide.txt
- ST_Quality_Report.txt
- configs/
- template_source/

## 四、注意事项

这个工具是工程辅助工具，不替代 PLC 工程师。

最终投产前必须完成 IO 地址复核、设备动作安全评审、单步调试、空跑验证、带料验证、急停和安全门测试。
""")

    write_text(RELEASE_NOTES, """
# Release Notes - V0.7.0

## 版本名称

PLC数字工程师 V0.7.0 最终成品封装版

## 基于版本

- V0.6.5 成品版网页操作台
- V0.6.4 工程质量增强核心
- V0.6.3 Sysmac Studio 导入前工程规范增强
- V0.6.2.2 Streamlit 界面端集成验收版

## V0.7.0 新增内容

- 页面版本升级为 V0.7.0
- 新增 README_PRODUCT_V070.md
- 新增 USER_MANUAL_V070.md
- 新增 RELEASE_NOTES_V070.md
- 新增 start_plc_digital_engineer_v070.bat
- 新增 release/PLC_Digital_Engineer_V070 发布目录
- 新增 PLC_Digital_Engineer_V070_Release.zip 发布包
- 新增 check_v070_release.py 发布验收脚本

## 当前状态

V0.7.0 是可演示、可测试、可继续迭代的成品封装版。

## 重要限制

- 暂未直接生成 Sysmac Studio 原生工程文件
- 生成的是导入前 ST / CSV / TXT 工程包
- 仍需 PLC 工程师进行最终确认
- 不可跳过现场安全调试
""")


def generate_start_bat():
    write_text(START_BAT, """
@echo off
cd /d D:\\AI\\plc_ai_system
streamlit run app_product.py
pause
""")


def generate_check_script():
    write_text(CHECK_SCRIPT, """
from pathlib import Path
import zipfile
import py_compile
import json

PROJECT_DIR = Path(r"D:\\AI\\plc_ai_system")
APP_PRODUCT = PROJECT_DIR / "app_product.py"
RELEASE_DIR = PROJECT_DIR / "release" / "PLC_Digital_Engineer_V070"
RELEASE_ZIP = PROJECT_DIR / "release" / "PLC_Digital_Engineer_V070_Release.zip"
FINAL_PRODUCT_ZIP = PROJECT_DIR / "output" / "AI_Device_Project_Package_V070_Final.zip"
BASE_PROJECT_ZIP = PROJECT_DIR / "output" / "AI_Device_Project_Package_V06.zip"

REQUIRED_PROJECT_FILES = [
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

REQUIRED_RELEASE_FILES = [
    "app_product.py",
    "start_plc_digital_engineer_v070.bat",
    "README_PRODUCT_V070.md",
    "USER_MANUAL_V070.md",
    "RELEASE_NOTES_V070.md",
    "START_HERE.txt",
]


def find_endswith(names, suffix):
    for n in names:
        if n.replace("\\\\", "/").endswith(suffix):
            return n
    return None


def read_text_from_zip(z, name):
    raw = z.read(name)
    for enc in ["utf-8-sig", "utf-8", "gbk"]:
        try:
            return raw.decode(enc)
        except Exception:
            pass
    return raw.decode("utf-8", errors="ignore")


def check_project_zip(zip_path):
    ok = True

    if not zip_path.exists():
        print("❌ 工程包不存在：", zip_path)
        return False

    print("工程包：", zip_path)

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

        for f in REQUIRED_PROJECT_FILES:
            if find_endswith(names, f):
                print(f"✅ {f}")
            else:
                print(f"❌ 缺少：{f}")
                ok = False

        manifest_name = find_endswith(names, "manifest.json")
        if manifest_name:
            manifest_text = read_text_from_zip(z, manifest_name)
            manifest = json.loads(manifest_text)
            print("generator_version =", manifest.get("generator_version"))
            print("version =", manifest.get("version"))

            if "V0.6.4" in manifest_text:
                print("✅ manifest 包含 V0.6.4 核心生成器信息")
            else:
                print("❌ manifest 缺少 V0.6.4")
                ok = False

        final_name = find_endswith(names, "Final_Acceptance_Report.txt")
        if final_name:
            final_text = read_text_from_zip(z, final_name)
            if "PASS" in final_text:
                print("✅ Final_Acceptance_Report 包含 PASS")
            else:
                print("❌ Final_Acceptance_Report 缺少 PASS")
                ok = False

    return ok


def main():
    print("========== V0.7.0 最终发布验收 ==========")

    ok = True

    print("\\n========== 1. app_product.py 检查 ==========")
    if APP_PRODUCT.exists():
        print("✅ app_product.py 存在")
    else:
        print("❌ app_product.py 不存在")
        return

    try:
        py_compile.compile(str(APP_PRODUCT), doraise=True)
        print("✅ app_product.py 语法检查通过")
    except Exception as e:
        print("❌ app_product.py 语法错误：", e)
        return

    app_text = APP_PRODUCT.read_text(encoding="utf-8", errors="ignore")
    for kw in ["V0.7.0", "PLC数字工程师", "AI解析整机需求", "人工确认", "最终工程包 ZIP"]:
        if kw in app_text:
            print(f"✅ 页面包含：{kw}")
        else:
            print(f"❌ 页面缺少：{kw}")
            ok = False

    print("\\n========== 2. 后端生成器检查 ==========")
    try:
        from company_generators.multi_station_project_generator import generate_multi_station_project_package_from_file
        result = generate_multi_station_project_package_from_file()
        print("生成结果：", result.get("ok"))
        print("ZIP：", result.get("zip_path"))
        if not result.get("ok"):
            ok = False
    except Exception as e:
        print("❌ 后端生成器运行失败：", e)
        ok = False

    print("\\n========== 3. 最终工程包 ZIP 检查 ==========")
    project_zip = FINAL_PRODUCT_ZIP if FINAL_PRODUCT_ZIP.exists() else BASE_PROJECT_ZIP
    if not check_project_zip(project_zip):
        ok = False

    print("\\n========== 4. 发布目录检查 ==========")
    if RELEASE_DIR.exists():
        print("✅ 发布目录存在：", RELEASE_DIR)
    else:
        print("❌ 发布目录不存在：", RELEASE_DIR)
        ok = False

    for f in REQUIRED_RELEASE_FILES:
        p = RELEASE_DIR / f
        if p.exists():
            print(f"✅ 发布目录包含：{f}")
        else:
            print(f"❌ 发布目录缺少：{f}")
            ok = False

    for folder in ["company_generators", "configs", "company_template", "sample_output"]:
        p = RELEASE_DIR / folder
        if p.exists():
            print(f"✅ 发布目录包含：{folder}")
        else:
            print(f"❌ 发布目录缺少：{folder}")
            ok = False

    print("\\n========== 5. Release ZIP 检查 ==========")
    if RELEASE_ZIP.exists():
        print("✅ Release ZIP 存在：", RELEASE_ZIP)
        print("大小 bytes：", RELEASE_ZIP.stat().st_size)
    else:
        print("❌ Release ZIP 不存在")
        ok = False

    if RELEASE_ZIP.exists():
        with zipfile.ZipFile(RELEASE_ZIP, "r") as z:
            names = z.namelist()
            for f in [
                "PLC_Digital_Engineer_V070/app_product.py",
                "PLC_Digital_Engineer_V070/start_plc_digital_engineer_v070.bat",
                "PLC_Digital_Engineer_V070/README_PRODUCT_V070.md",
                "PLC_Digital_Engineer_V070/USER_MANUAL_V070.md",
                "PLC_Digital_Engineer_V070/RELEASE_NOTES_V070.md",
            ]:
                if f in names:
                    print(f"✅ Release ZIP 包含：{f}")
                else:
                    print(f"❌ Release ZIP 缺少：{f}")
                    ok = False

    print("\\n========== V0.7.0 最终验收结论 ==========")
    if ok:
        print("✅ V0.7.0 最终成品封装版验收通过")
        print("启动命令：streamlit run app_product.py")
        print("发布包：", RELEASE_ZIP)
    else:
        print("❌ V0.7.0 仍有问题，请把完整输出发给我")


if __name__ == "__main__":
    main()
""")


def generate_sample_project_zip():
    print("========== 生成 V0.7.0 示例最终工程包 ==========")

    try:
        from company_generators.multi_station_project_generator import generate_multi_station_project_package_from_file
        result = generate_multi_station_project_package_from_file()
    except Exception as e:
        print("❌ 调用后端生成器失败：", e)
        return False

    if not result.get("ok"):
        print("❌ 示例工程包生成失败：", result)
        return False

    if BASE_PROJECT_ZIP.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BASE_PROJECT_ZIP, FINAL_PRODUCT_ZIP)
        print("✅ 示例最终工程包：", FINAL_PRODUCT_ZIP)
        return True

    print("❌ 没找到基础工程包：", BASE_PROJECT_ZIP)
    return False


def copy_dir(src: Path, dst: Path):
    if not src.exists():
        print("⚠️ 跳过不存在目录：", src)
        return

    if dst.exists():
        shutil.rmtree(dst)

    ignore = shutil.ignore_patterns(
        "__pycache__",
        "*.pyc",
        ".venv",
        "venv",
        "env",
        "*.zip",
        "*backup*",
    )

    shutil.copytree(src, dst, ignore=ignore)
    print("✅ 复制目录：", src, "→", dst)


def build_release_dir():
    print("========== 构建发布目录 ==========")

    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    files = [
        APP_PRODUCT,
        START_BAT,
        PRODUCT_README,
        USER_MANUAL,
        RELEASE_NOTES,
        CHECK_SCRIPT,
    ]

    for f in files:
        if f.exists():
            shutil.copy2(f, RELEASE_DIR / f.name)
            print("✅ 复制文件：", f.name)
        else:
            print("⚠️ 文件不存在，跳过：", f)

    copy_dir(GEN_DIR, RELEASE_DIR / "company_generators")
    copy_dir(PROJECT_DIR / "configs", RELEASE_DIR / "configs")
    copy_dir(PROJECT_DIR / "company_template", RELEASE_DIR / "company_template")

    sample_dir = RELEASE_DIR / "sample_output"
    sample_dir.mkdir(parents=True, exist_ok=True)

    if FINAL_PRODUCT_ZIP.exists():
        shutil.copy2(FINAL_PRODUCT_ZIP, sample_dir / FINAL_PRODUCT_ZIP.name)
        print("✅ 复制示例工程包：", FINAL_PRODUCT_ZIP.name)
    elif BASE_PROJECT_ZIP.exists():
        shutil.copy2(BASE_PROJECT_ZIP, sample_dir / "AI_Device_Project_Package_V070_Final.zip")
        print("✅ 复制示例工程包：AI_Device_Project_Package_V070_Final.zip")

    write_text(RELEASE_DIR / "START_HERE.txt", """
PLC数字工程师 V0.7.0

启动方式：

1. 确认电脑已安装 Python、Streamlit 和项目依赖。
2. 双击 start_plc_digital_engineer_v070.bat。
3. 或在命令行运行：

cd /d D:\\AI\\plc_ai_system
streamlit run app_product.py

sample_output 目录里是示例生成的最终工程包。
""")

    print("✅ 发布目录构建完成：", RELEASE_DIR)


def build_release_zip():
    print("========== 打包 Release ZIP ==========")

    RELEASE_ZIP.parent.mkdir(parents=True, exist_ok=True)

    if RELEASE_ZIP.exists():
        RELEASE_ZIP.unlink()

    with zipfile.ZipFile(RELEASE_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for file in RELEASE_DIR.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(RELEASE_DIR.parent)
                z.write(file, arcname)

    print("✅ 最终发布包：", RELEASE_ZIP)


def main():
    print("========== 安装 V0.7.0 Final Release ==========")

    if not PROJECT_DIR.exists():
        print("❌ 项目目录不存在：", PROJECT_DIR)
        return

    if not GEN_DIR.exists():
        print("❌ company_generators 不存在，请先完成前置版本")
        return

    if not patch_app_product():
        return

    generate_docs()
    generate_start_bat()
    generate_check_script()
    generate_sample_project_zip()
    build_release_dir()
    build_release_zip()

    print("\n========== 安装结果 ==========")
    print("✅ V0.7.0 最终成品封装安装完成")
    print("下一步运行：")
    print("python check_v070_release.py")
    print("")
    print("启动成品版：")
    print("streamlit run app_product.py")
    print("")
    print("最终发布包：")
    print(RELEASE_ZIP)


if __name__ == "__main__":
    main()