(*
================================================================================
 File    : 05_Servo_Axis_Generated.st
 Version : V0.7.1
 Purpose : 伺服轴基础控制逻辑建议
 Time    : 2026-05-08 06:49:17
================================================================================
*)

// 注意：以下为伺服控制逻辑框架。
// 正式使用前需要在 Sysmac Studio 中绑定真实 Axis 轴对象，
// 并由 PLC 工程师替换为 MC_Power / MC_Home / MC_MoveAbsolute / MC_Stop 等真实运动控制指令。

// ================================================================
// Axis[1] - X轴
// ================================================================
Axis[1].rVelocity := 200.0;
Axis[1].rAcceleration := 1000.0;
Axis[1].rDeceleration := 1000.0;

IF Machine_Data.IN.bReset THEN
    Axis[1].bReset := TRUE;
    Axis[1].bAlarm := FALSE;
    Axis[1].nAlarmNo := 0;
    Axis[1].bDone := FALSE;
    Axis[1].bBusy := FALSE;
END_IF;

// 伺服报警时禁止整机运行
IF Axis[1].bAlarm THEN
    Machine_Auto.bCanRun := FALSE;
    Machine_Auto.bAnyStationAlarm := TRUE;
END_IF;

// Servo On 框架
IF Axis[1].bServoOn AND NOT Axis[1].bAlarm THEN
    // TODO: 调用 MC_Power
END_IF;

// Home 框架
IF Axis[1].bHome AND NOT Axis[1].bAlarm THEN
    Axis[1].bBusy := TRUE;
    // TODO: 调用 MC_Home
    // Home 完成后：Axis[1].bHomeDone := TRUE;
END_IF;

// Move Absolute 框架
IF Axis[1].bMoveAbs AND Axis[1].bHomeDone AND NOT Axis[1].bAlarm THEN
    Axis[1].bBusy := TRUE;
    // TODO: 调用 MC_MoveAbsolute
    // Position := Axis[1].rTargetPosition
    // Velocity := Axis[1].rVelocity
END_IF;

// Jog Positive / Negative 框架
IF Axis[1].bJogPositive AND NOT Axis[1].bAlarm THEN
    // TODO: 调用 MC_MoveVelocity 正方向
END_IF;

IF Axis[1].bJogNegative AND NOT Axis[1].bAlarm THEN
    // TODO: 调用 MC_MoveVelocity 负方向
END_IF;

// Stop 框架
IF Axis[1].bStop OR Machine_Data.IN.bEstop THEN
    // TODO: 调用 MC_Stop / MC_Halt
    Axis[1].bBusy := FALSE;
END_IF;
