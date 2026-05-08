// ==================================================
// S1_Auto_Generated - 公司工站模板生成版
// 工站名称：S1_工站名称
// 由 PLC数字工程师 根据公司模板自动生成
// ==================================================

PROGRAM S1_Auto_Generated

VAR
    _StationNum : INT := 1;
    bRunAble    : BOOL;
END_VAR


// ==================================================
// 工站运行条件
// ==================================================
bRunAble := Machine_Data.IN.bEStop AND Machine_Data.IN.bSafety AND Machine_Data.IN.bAirOn;

IF NOT bRunAble THEN
    Station[_StationNum].bEstop := TRUE;
    Station[_StationNum].bRunning := FALSE;
    Station[_StationNum].nAutoStep := 999;
END_IF;

IF Machine_Data.bReset THEN
    Station[_StationNum].bEstop := FALSE;
END_IF;


// ==================================================
// 工站自动流程
// ==================================================
CASE Station[_StationNum].nAutoStep OF

    0: // INIT 初始化
        Cylinder_Data.CY1.Input.bAuto:=FALSE;
        Cylinder_Data.CY2.Input.bAuto:=FALSE;

        IF bRunAble THEN
            Station[_StationNum].nAutoStep := 10;
        END_IF;

    10: // 等待启动
        // No action

        IF bRunAble AND Station[_StationNum].bRunning THEN
            Station[_StationNum].nAutoStep := 20;
        END_IF;

    20: // CY1拨料上下气缸到动点
        Cylinder_Data.CY1.Input.bAuto:=TRUE;

        IF Cylinder_Data.CY1.Output.bWP_Delay THEN
            Station[_StationNum].nAutoStep := 30;
        END_IF;

    30: // CY2 NG剔除气缸到动点
        Cylinder_Data.CY2.Input.bAuto:=TRUE;

        IF Cylinder_Data.CY2.Output.bWP_Delay THEN
            Station[_StationNum].nAutoStep := 40;
        END_IF;

    40: // CY2回原点
        Cylinder_Data.CY2.Input.bAuto:=FALSE;

        IF Cylinder_Data.CY2.Output.bHP_Delay THEN
            Station[_StationNum].nAutoStep := 50;
        END_IF;

    50: // CY1回原点
        Cylinder_Data.CY1.Input.bAuto:=FALSE;

        IF Cylinder_Data.CY1.Output.bHP_Delay THEN
            Station[_StationNum].nAutoStep := 60;
        END_IF;

    60: // 流程完成，回到等待启动
        // No action

        IF bRunAble AND Station[_StationNum].bRunning THEN
            Station[_StationNum].nAutoStep := 10;
        END_IF;

    999: // 报警停机
        // No action

    ELSE
        Station[_StationNum].nAutoStep := 999;

END_CASE;

END_PROGRAM
