import json
import shutil
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path

from company_generators.cylinder_generator import (
    render_cylinder_action,
    validate_all_cylinders
)

from company_generators.station_generator import (
    render_station_program,
    validate_station_config
)

from company_generators.project_validator import build_validation_report


GENERATOR_NAME = "PLC数字工程师"
GENERATOR_VERSION = "V0.4.2"
TEMPLATE_VERSION = "company_template_v0.1"

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "configs"
OUTPUT_DIR = BASE_DIR / "output"

DEFAULT_CYLINDER_CONFIG = CONFIG_DIR / "sample_cylinders.json"
DEFAULT_STATION_CONFIG = CONFIG_DIR / "sample_station.json"
DEFAULT_SYMBOL_CONFIG = CONFIG_DIR / "company_symbols.json"

PACKAGE_DIR = OUTPUT_DIR / "device_project_package"
ZIP_PATH = OUTPUT_DIR / "AI_Device_Project_Package.zip"


def load_json_file(path: str | Path) -> dict:
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def file_sha256(path: Path) -> str:
    sha256 = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def build_file_record(file: Path, package_dir: Path, category: str) -> dict:
    return {
        "path": str(file.relative_to(package_dir)).replace("\\", "/"),
        "category": category,
        "size_bytes": file.stat().st_size,
        "sha256": file_sha256(file)
    }


def build_readme(project_info: dict) -> str:
    project_name = project_info.get("project_name", "AI_Device_Project")
    plc = project_info.get("plc", "Omron NJ501")
    description = project_info.get("description", "")

    return f"""
PLC数字工程师 {GENERATOR_VERSION} 工程包

项目名称：{project_name}
PLC：{plc}
生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
生成器：{GENERATOR_NAME}
模板版本：{TEMPLATE_VERSION}

项目说明：
{description}

文件说明：
1. 00_README.txt
   - 工程包说明文件

2. validation_report.txt
   - 自动校验报告
   - 检查气缸配置、工站配置、报警配置、模板源文件、公司符号配置等

3. manifest.json
   - 工程包清单
   - 记录生成器版本、生成时间、文件列表、文件大小、SHA256校验值

4. 01_Cylinder_Action_Generated.st
   - 公司模板风格气缸动作调用程序
   - 由 configs/cylinder_config.json 渲染生成

5. 02_Station_Generated.st
   - 公司模板风格工站自动流程程序
   - 包含 Station[_StationNum].nAutoStep
   - 支持超时报警、安全停机、完成复位
   - 由 configs/station_config.json 渲染生成

6. configs/cylinder_config.json
   - 气缸配置

7. configs/station_config.json
   - 工站流程配置

8. configs/company_symbols.json
   - 公司命名配置
   - 修改这里可以适配不同项目字段名

9. template_source/
   - 从公司原始项目提取出的模板参考文件

注意：
- 本工程包为自动生成模板，不能直接下载到真实PLC。
- 必须经过工程师审核、Sysmac Studio 编译、仿真、空载验证、现场调试。
- 急停、安全门、光栅等安全功能必须走硬件安全回路。
- manifest.json 仅用于追踪生成信息，不代表程序已通过现场验证。
- validation_report.txt 仅为基础规则校验，不能替代工程师审核。
""".strip()


def build_manifest(
    project_info: dict,
    package_dir: Path,
    file_records: list[dict],
    cylinder_config: dict,
    station_config: dict
) -> dict:
    project_name = project_info.get("project_name", "AI_Device_Project")
    plc = project_info.get("plc", "Omron NJ501")
    description = project_info.get("description", "")

    cylinders = cylinder_config.get("cylinders", [])
    steps = station_config.get("steps", [])

    return {
        "manifest_version": "1.0",
        "generator": GENERATOR_NAME,
        "generator_version": GENERATOR_VERSION,
        "template_version": TEMPLATE_VERSION,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project": {
            "project_name": project_name,
            "plc": plc,
            "description": description
        },
        "summary": {
            "cylinder_count": len(cylinders),
            "station_step_count": len(steps),
            "has_company_symbols": (package_dir / "configs" / "company_symbols.json").exists(),
            "has_template_source": (package_dir / "template_source").exists(),
            "has_validation_report": (package_dir / "validation_report.txt").exists()
        },
        "generated_outputs": [
            item for item in file_records
            if item["category"] == "generated_st"
        ],
        "configs": [
            item for item in file_records
            if item["category"] == "config"
        ],
        "template_source": [
            item for item in file_records
            if item["category"] == "template_source"
        ],
        "documents": [
            item for item in file_records
            if item["category"] == "document"
        ],
        "all_files": file_records
    }


def generate_project_package(
    cylinder_config: dict,
    station_config: dict,
    project_info: dict | None = None,
    package_dir: Path = PACKAGE_DIR,
    zip_path: Path = ZIP_PATH
) -> dict:
    if project_info is None:
        project_info = {
            "project_name": "AI_Device_Project",
            "plc": "Omron NJ501",
            "description": "PLC数字工程师生成工程包"
        }

    errors = []

    cylinders = cylinder_config.get("cylinders", [])

    if not cylinders:
        errors.append("cylinder_config 中没有 cylinders。")
    else:
        errors.extend(validate_all_cylinders(cylinders))

    errors.extend(validate_station_config(station_config))

    if errors:
        return {
            "ok": False,
            "errors": errors,
            "package_dir": None,
            "zip_path": None,
            "files": [],
            "manifest": None
        }

    cylinder_code = render_cylinder_action(cylinders)
    station_code = render_station_program(station_config)
    readme = build_readme(project_info)

    if package_dir.exists():
        shutil.rmtree(package_dir)

    package_dir.mkdir(parents=True, exist_ok=True)

    files_written: list[tuple[Path, str]] = []

    readme_path = package_dir / "00_README.txt"
    validation_path = package_dir / "validation_report.txt"
    cylinder_path = package_dir / "01_Cylinder_Action_Generated.st"
    station_path = package_dir / "02_Station_Generated.st"

    write_text(readme_path, readme)
    write_text(cylinder_path, cylinder_code)
    write_text(station_path, station_code)

    files_written.extend([
        (readme_path, "document"),
        (cylinder_path, "generated_st"),
        (station_path, "generated_st")
    ])

    configs_dir = package_dir / "configs"

    cylinder_config_path = configs_dir / "cylinder_config.json"
    station_config_path = configs_dir / "station_config.json"

    write_text(
        cylinder_config_path,
        json.dumps(cylinder_config, ensure_ascii=False, indent=4)
    )
    write_text(
        station_config_path,
        json.dumps(station_config, ensure_ascii=False, indent=4)
    )

    files_written.extend([
        (cylinder_config_path, "config"),
        (station_config_path, "config")
    ])

    if DEFAULT_SYMBOL_CONFIG.exists():
        symbols_text = DEFAULT_SYMBOL_CONFIG.read_text(encoding="utf-8")
        symbols_path = configs_dir / "company_symbols.json"
        write_text(symbols_path, symbols_text)
        files_written.append((symbols_path, "config"))

    template_dir = package_dir / "template_source"
    company_st_dir = BASE_DIR / "company_template" / "st"

    template_files = [
        "FB_Cylinder.st",
        "Cylinder_Action.st",
        "MachineAlarm.st",
        "Machine_Init.st",
        "Servo_Action.st",
        "FB_Axis.st",
        "FB_Motor.st",
        "FB_Delay.st",
        "FB_SafetyDoor.st",
        "FB_Vacuum.st"
    ]

    for filename in template_files:
        src = company_st_dir / filename
        if src.exists():
            dst = template_dir / filename
            write_text(dst, src.read_text(encoding="utf-8"))
            files_written.append((dst, "template_source"))

    validation_report = build_validation_report(
        cylinder_config=cylinder_config,
        station_config=station_config,
        project_info=project_info,
        package_dir=package_dir
    )

    write_text(validation_path, validation_report)
    files_written.append((validation_path, "document"))

    file_records = [
        build_file_record(path, package_dir, category)
        for path, category in files_written
    ]

    manifest = build_manifest(
        project_info=project_info,
        package_dir=package_dir,
        file_records=file_records,
        cylinder_config=cylinder_config,
        station_config=station_config
    )

    manifest_path = package_dir / "manifest.json"

    write_text(
        manifest_path,
        json.dumps(manifest, ensure_ascii=False, indent=4)
    )

    files_written.append((manifest_path, "manifest"))

    manifest_record = build_file_record(manifest_path, package_dir, "manifest")
    file_records.append(manifest_record)

    manifest["manifest_file"] = manifest_record
    manifest["all_files"] = file_records

    write_text(
        manifest_path,
        json.dumps(manifest, ensure_ascii=False, indent=4)
    )

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file, _category in files_written:
            arcname = file.relative_to(package_dir)
            zip_file.write(file, arcname)

    return {
        "ok": True,
        "errors": [],
        "package_dir": str(package_dir),
        "zip_path": str(zip_path),
        "files": [str(f) for f, _category in files_written],
        "manifest": manifest
    }


def generate_project_package_from_files() -> dict:
    cylinder_config = load_json_file(DEFAULT_CYLINDER_CONFIG)
    station_config = load_json_file(DEFAULT_STATION_CONFIG)

    project_info = {
        "project_name": "AI_Device_Project_V042",
        "plc": "Omron NJ501",
        "description": "由气缸配置和工站配置合并生成的完整设备工程包，包含 manifest 追踪清单和 validation_report 自动校验报告。"
    }

    return generate_project_package(
        cylinder_config=cylinder_config,
        station_config=station_config,
        project_info=project_info
    )


def main():
    result = generate_project_package_from_files()

    if not result["ok"]:
        print("工程包生成失败：")
        for err in result["errors"]:
            print(" -", err)
        return

    print("工程包生成成功：")
    print("目录：", result["package_dir"])
    print("ZIP：", result["zip_path"])
    print("")
    print("文件列表：")
    for f in result["files"]:
        print(" -", f)

    print("")
    print("manifest.json 已生成。")
    print("validation_report.txt 已生成。")


if __name__ == "__main__":
    main()