(*
================================================================================
 File    : 00_DUT_Struct_Generated.st
 Version : V0.6.3
 Author  : PLC Digital Engineer AI
 Time    : 2026-05-08 06:49:17

 Purpose : Sysmac Studio 导入前 DUT / STRUCT 类型声明
================================================================================
*)

TYPE

    ST_CylinderIO : STRUCT
        bOriginSensor : BOOL;
        bWorkSensor   : BOOL;
        bOriginValve  : BOOL;
        bWorkValve    : BOOL;
    END_STRUCT;

    ST_CylinderCtrl : STRUCT
        bCmdToOrigin  : BOOL;
        bCmdToWork    : BOOL;
        bBusy         : BOOL;
        bDone         : BOOL;
        bAlarm        : BOOL;
        nAlarmNo      : INT;
    END_STRUCT;

    ST_StationAuto : STRUCT
        nAutoStep : INT;
        bEnable   : BOOL;
        bRunning  : BOOL;
        bDone     : BOOL;
        bEstop    : BOOL;
    END_STRUCT;

    ST_MachineAuto : STRUCT
        bReady           : BOOL;
        bCanRun          : BOOL;
        bAnyStationAlarm : BOOL;
        bComplete        : BOOL;
    END_STRUCT;

    ST_StationAlarm : STRUCT
        Alarm   : BOOL;
        AlarmNo : INT;
    END_STRUCT;

    ST_MachineAlarm : STRUCT
        StationAlarm : ARRAY[1..2] OF ST_StationAlarm;
    END_STRUCT;

    ST_MachineDataIN : STRUCT
        bEstop  : BOOL;
        bSafety : BOOL;
        bAirOn  : BOOL;
        bReset  : BOOL;
    END_STRUCT;

    ST_MachineData : STRUCT
        IN : ST_MachineDataIN;
    END_STRUCT;

END_TYPE

(*
推荐数组规模：
- Station       : ARRAY[1..2] OF ST_StationAuto
- CylinderIO    : ARRAY[1..2] OF ST_CylinderIO
- CylinderCtrl  : ARRAY[1..2] OF ST_CylinderCtrl
*)
