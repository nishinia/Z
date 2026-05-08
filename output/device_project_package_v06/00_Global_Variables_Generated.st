(*
================================================================================
 File    : 00_Global_Variables_Generated.st
 Version : V0.6.3
 Author  : PLC Digital Engineer AI
 Time    : 2026-05-08 06:49:17

 Purpose : Sysmac Studio 全局变量声明建议
================================================================================
*)

VAR_GLOBAL
    // 整机状态
    Machine_Auto  : ST_MachineAuto;
    Machine_Data  : ST_MachineData;
    Machine_Alarm : ST_MachineAlarm;

    // 工站状态
    Station : ARRAY[1..2] OF ST_StationAuto;

    // 气缸 IO / 控制
    CylinderIO   : ARRAY[1..2] OF ST_CylinderIO;
    CylinderCtrl : ARRAY[1..2] OF ST_CylinderCtrl;
END_VAR

(*
工站索引：
- Station[1] = S1 / S1_上料工站
- Station[2] = S2 / S2_搬运工站

气缸索引：
- CylinderIO[1] / CylinderCtrl[1] = CY1 / CY1气缸
- CylinderIO[2] / CylinderCtrl[2] = CY2 / CY2气缸
*)
