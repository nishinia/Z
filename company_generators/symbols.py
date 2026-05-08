import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SYMBOL_CONFIG_PATH = BASE_DIR / "configs" / "company_symbols.json"


DEFAULT_SYMBOLS = {
    "machine_estop": "Machine_Data.IN.bEStop",
    "machine_safety": "Machine_Data.IN.bSafety",
    "machine_air": "Machine_Data.IN.bAirOn",
    "machine_reset": "Machine_Data.bReset",

    "station_step": "Station[_StationNum].nAutoStep",
    "station_running": "Station[_StationNum].bRunning",
    "station_estop": "Station[_StationNum].bEstop",

    "station_alarm_base": "Machine_Alarm.StationAlarm[_StationNum].Alarm"
}


def load_company_symbols() -> dict:
    if not SYMBOL_CONFIG_PATH.exists():
        return DEFAULT_SYMBOLS.copy()

    try:
        data = json.loads(SYMBOL_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_SYMBOLS.copy()

    symbols = DEFAULT_SYMBOLS.copy()
    symbols.update(data)
    return symbols


def build_default_run_condition(symbols: dict) -> str:
    return (
        f'{symbols["machine_estop"]} AND '
        f'{symbols["machine_safety"]} AND '
        f'{symbols["machine_air"]}'
    )


def build_alarm_bit(symbols: dict, alarm_no: int | str) -> str:
    return f'{symbols["station_alarm_base"]}[{alarm_no}]'