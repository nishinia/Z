(*
================================================================================
 File    : 04_Machine_Auto_Main_Generated.st
 Version : V0.6.2.1
 Author  : PLC Digital Engineer AI
 Time    : 2026-05-08 06:49:17

 Purpose : 整机主流程 / 多工站互锁 / 报警汇总 / 统一复位
================================================================================
*)

// ================================================================
// 1. 整机基础运行条件
// ================================================================
Machine_Auto.bReady := Machine_Data.IN.bSafety
                       AND Machine_Data.IN.bAirOn
                       AND NOT Machine_Data.IN.bEstop;

// 所有工站报警汇总
Machine_Auto.bAnyStationAlarm :=
    Machine_Alarm.StationAlarm[1].Alarm OR
    Machine_Alarm.StationAlarm[2].Alarm;

Machine_Auto.bCanRun := Machine_Auto.bReady
                       AND NOT Machine_Auto.bAnyStationAlarm;

// ================================================================
// 2. 统一复位逻辑
// ================================================================
IF Machine_Data.IN.bReset THEN
    Machine_Auto.bComplete := FALSE;
    Machine_Auto.bAnyStationAlarm := FALSE;
    Machine_Auto.bCanRun := FALSE;

    // Reset S1 - S1_上料工站
    Station[1].nAutoStep := 0;
    Station[1].bEnable := FALSE;
    Station[1].bRunning := FALSE;
    Station[1].bDone := FALSE;
    Station[1].bEstop := FALSE;
    Machine_Alarm.StationAlarm[1].Alarm := FALSE;
    Machine_Alarm.StationAlarm[1].AlarmNo := 0;

    // Reset S2 - S2_搬运工站
    Station[2].nAutoStep := 0;
    Station[2].bEnable := FALSE;
    Station[2].bRunning := FALSE;
    Station[2].bDone := FALSE;
    Station[2].bEstop := FALSE;
    Machine_Alarm.StationAlarm[2].Alarm := FALSE;
    Machine_Alarm.StationAlarm[2].AlarmNo := 0;

END_IF;

// ================================================================
// 3. 多工站顺序互锁
// ================================================================
// S1 - S1_上料工站
Station[1].bEnable := Machine_Auto.bCanRun;
Station[1].bEstop := NOT Station[1].bEnable;

// S2 - S2_搬运工站
Station[2].bEnable := Machine_Auto.bCanRun
                       AND Station[1].bDone;
Station[2].bEstop := NOT Station[2].bEnable;

// ================================================================
// 4. 整机完成判断
// ================================================================
Machine_Auto.bComplete := Station[2].bDone;

// ================================================================
// 5. HMI 推荐显示状态
// ================================================================
// Machine_Auto.bReady           : 整机就绪
// Machine_Auto.bCanRun          : 整机允许运行
// Machine_Auto.bAnyStationAlarm : 任意工站报警
// Machine_Auto.bComplete        : 整机完成
