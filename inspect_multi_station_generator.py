from pathlib import Path
import ast

TARGET = Path(r"D:\AI\plc_ai_system\company_generators\multi_station_project_generator.py")

def main():
    if not TARGET.exists():
        print("❌ 文件不存在：", TARGET)
        return

    text = TARGET.read_text(encoding="utf-8", errors="ignore")

    print("========== 文件路径 ==========")
    print(TARGET)

    print("\n========== 文件前 80 行 ==========")
    lines = text.splitlines()
    for i, line in enumerate(lines[:80], start=1):
        print(f"{i:03d}: {line}")

    print("\n========== 顶层函数 ==========")
    try:
        tree = ast.parse(text)
        funcs = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
        if funcs:
            for f in funcs:
                print("函数：", f)
        else:
            print("⚠️ 没找到顶层函数")
    except Exception as e:
        print("❌ AST 解析失败：", e)

    print("\n========== 是否已接入 V0.6.2.1 ==========")
    checks = [
        "machine_main_generator",
        "hmi_variable_generator",
        "generate_machine_main_st",
        "generate_hmi_variable_csv",
        "04_Machine_Auto_Main_Generated.st",
        "HMI_Variable_List.csv",
    ]

    for kw in checks:
        if kw in text:
            print(f"✅ 已包含：{kw}")
        else:
            print(f"❌ 未包含：{kw}")

if __name__ == "__main__":
    main()