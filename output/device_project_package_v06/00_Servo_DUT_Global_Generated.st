(*
================================================================================
 File    : 00_Servo_DUT_Global_Generated.st
 Version : V0.7.1
 Purpose : 伺服轴 DUT / 全局变量建议
 Time    : 2026-05-08 06:49:17
================================================================================
*)

TYPE
    ST_AxisAuto : STRUCT
        bServoOn        : BOOL;
        bHome           : BOOL;
        bHomeDone       : BOOL;
        bJogPositive    : BOOL;
        bJogNegative    : BOOL;
        bMoveAbs        : BOOL;
        bMoveRel        : BOOL;
        bStop           : BOOL;
        bReset          : BOOL;
        bBusy           : BOOL;
        bDone           : BOOL;
        bAlarm          : BOOL;
        nAlarmNo        : INT;
        rActualPosition : LREAL;
        rTargetPosition : LREAL;
        rVelocity       : LREAL;
        rAcceleration   : LREAL;
        rDeceleration   : LREAL;
    END_STRUCT;

    ST_AxisPoint : STRUCT
        nPointNo  : INT;
        sPointName : STRING[32];
        rPosition : LREAL;
        rVelocity : LREAL;
    END_STRUCT;
END_TYPE

VAR_GLOBAL
    Axis      : ARRAY[1..1] OF ST_AxisAuto;
    AxisPoint : ARRAY[1..1, 1..3] OF ST_AxisPoint;
END_VAR

(*
轴索引：
- Axis[1] = AX1 / X轴
*)
