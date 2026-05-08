from pathlib import Path

TARGET = Path(r"D:\AI\plc_ai_system\company_generators\multi_station_project_generator.py")

def main():
    text = TARGET.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    start = None
    end = None

    for i, line in enumerate(lines, start=1):
        if line.startswith("def generate_multi_station_project_package("):
            start = i
            break

    if start is None:
        print("❌ 没找到 generate_multi_station_project_package")
        return

    for i in range(start + 1, len(lines) + 1):
        line = lines[i - 1]
        if line.startswith("def ") and i > start:
            end = i - 1
            break

    if end is None:
        end = len(lines)

    print(f"========== generate_multi_station_project_package 函数，行 {start} 到 {end} ==========")

    for i in range(max(1, start - 10), min(len(lines), end + 10) + 1):
        print(f"{i:03d}: {lines[i - 1]}")

if __name__ == "__main__":
    main()