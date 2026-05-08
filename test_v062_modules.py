from company_generators.machine_main_generator import generate_machine_main_st
from company_generators.hmi_variable_generator import generate_hmi_variable_csv_text


def main():
    station_configs = [
        {
            "station_id": "S1",
            "station_name": "S1_上料工站",
        },
        {
            "station_id": "S2",
            "station_name": "S2_分拣工站",
        },
    ]

    machine_st = generate_machine_main_st(station_configs)
    hmi_csv = generate_hmi_variable_csv_text(station_configs)

    print("========== 04_Machine_Auto_Main_Generated.st 预览 ==========")
    print(machine_st[:2000])

    print("\n========== HMI_Variable_List.csv 预览 ==========")
    print(hmi_csv)

    assert "Station[1].bEnable" in machine_st
    assert "Station[2].bEnable" in machine_st
    assert "Station[1].bDone" in machine_st
    assert "Machine_Auto.bComplete" in machine_st
    assert "Machine_Auto.bAnyStationAlarm" in machine_st
    assert "Machine_Data.IN.bReset" in machine_st

    assert "Machine_Auto.bReady" in hmi_csv
    assert "Station[1].nAutoStep" in hmi_csv
    assert "Station[2].nAutoStep" in hmi_csv
    assert "Machine_Alarm.StationAlarm[1].Alarm" in hmi_csv
    assert "Machine_Alarm.StationAlarm[2].Alarm" in hmi_csv

    print("\n✅ V0.6.2.1 两个新增模块测试通过")


if __name__ == "__main__":
    main()