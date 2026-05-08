from pathlib import Path

APP = Path(r"D:\AI\plc_ai_system\app.py")

def print_range(start, end):
    text = APP.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    print(f"\n========== app.py 行 {start} 到 {end} ==========")

    for i in range(start, min(end, len(lines)) + 1):
        print(f"{i:04d}: {lines[i - 1]}")

def main():
    print_range(900, 1120)

if __name__ == "__main__":
    main()