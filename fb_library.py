FB_LIBRARY = r"""
// ==================================================
// FB_Conveyor 输送线函数块
// ==================================================
FUNCTION_BLOCK FB_Conveyor
VAR_INPUT
    Enable      : BOOL;
    StartCmd    : BOOL;
    StopCmd     : BOOL;
    EStopOK     : BOOL;
    DoorOK      : BOOL;
    AirOK       : BOOL;
    SensorJam   : BOOL;
    Reset       : BOOL;
END_VAR

VAR_OUTPUT
    MotorRun    : BOOL;
    Busy        : BOOL;
    AlarmJam    : BOOL;
    AlarmSafety : BOOL;
END_VAR

VAR
    M_RunLatch  : BOOL;
END_VAR

IF NOT EStopOK OR NOT DoorOK OR NOT AirOK THEN
    MotorRun := FALSE;
    Busy := FALSE;
    M_RunLatch := FALSE;
    AlarmSafety := TRUE;
ELSE
    AlarmSafety := FALSE;

    IF Reset THEN
        AlarmJam := FALSE;
    END_IF;

    IF SensorJam THEN
        AlarmJam := TRUE;
        M_RunLatch := FALSE;
    END_IF;

    IF Enable AND StartCmd AND NOT AlarmJam THEN
        M_RunLatch := TRUE;
    END_IF;

    IF StopCmd THEN
        M_RunLatch := FALSE;
    END_IF;

    MotorRun := M_RunLatch;
    Busy := M_RunLatch;
END_IF;

END_FUNCTION_BLOCK


// ==================================================
// FB_Scanner 扫码函数块
// ==================================================
FUNCTION_BLOCK FB_Scanner
VAR_INPUT
    Enable        : BOOL;
    Trigger       : BOOL;
    ScanDone      : BOOL;
    ScanOK        : BOOL;
    Reset         : BOOL;
    TimeoutLimit  : TIME;
END_VAR

VAR_OUTPUT
    TriggerOut    : BOOL;
    ResultOK      : BOOL;
    ResultNG      : BOOL;
    Busy          : BOOL;
    AlarmTimeout  : BOOL;
END_VAR

VAR
    T_Timeout     : TON;
    M_TriggerOld  : BOOL;
    M_Working     : BOOL;
END_VAR

IF Reset THEN
    TriggerOut := FALSE;
    ResultOK := FALSE;
    ResultNG := FALSE;
    Busy := FALSE;
    AlarmTimeout := FALSE;
    M_Working := FALSE;
END_IF;

IF Enable AND Trigger AND NOT M_TriggerOld THEN
    TriggerOut := TRUE;
    M_Working := TRUE;
    Busy := TRUE;
    ResultOK := FALSE;
    ResultNG := FALSE;
END_IF;

M_TriggerOld := Trigger;

T_Timeout(IN := M_Working, PT := TimeoutLimit);

IF ScanDone THEN
    TriggerOut := FALSE;
    Busy := FALSE;
    M_Working := FALSE;

    IF ScanOK THEN
        ResultOK := TRUE;
        ResultNG := FALSE;
    ELSE
        ResultOK := FALSE;
        ResultNG := TRUE;
    END_IF;
END_IF;

IF T_Timeout.Q THEN
    TriggerOut := FALSE;
    Busy := FALSE;
    M_Working := FALSE;
    AlarmTimeout := TRUE;
END_IF;

END_FUNCTION_BLOCK


// ==================================================
// FB_Diverter NG分拣气缸函数块
// ==================================================
FUNCTION_BLOCK FB_Diverter
VAR_INPUT
    Enable       : BOOL;
    CmdNG        : BOOL;
    CylHome      : BOOL;
    CylWork      : BOOL;
    Reset        : BOOL;
    TimeoutLimit : TIME;
END_VAR

VAR_OUTPUT
    Y_Extend     : BOOL;
    Y_Retract    : BOOL;
    Done         : BOOL;
    Busy         : BOOL;
    AlarmTimeout : BOOL;
END_VAR

VAR
    Step         : INT;
    T_Timeout    : TON;
END_VAR

IF Reset THEN
    Step := 0;
    Y_Extend := FALSE;
    Y_Retract := TRUE;
    Done := FALSE;
    Busy := FALSE;
    AlarmTimeout := FALSE;
END_IF;

CASE Step OF

    0:
        Done := FALSE;
        Busy := FALSE;
        Y_Extend := FALSE;
        Y_Retract := TRUE;

        IF Enable AND CmdNG THEN
            Step := 10;
        END_IF;

    10:
        Busy := TRUE;
        Y_Extend := TRUE;
        Y_Retract := FALSE;

        IF CylWork THEN
            Step := 20;
        END_IF;

    20:
        Y_Extend := FALSE;
        Y_Retract := TRUE;

        IF CylHome THEN
            Done := TRUE;
            Busy := FALSE;
            Step := 0;
        END_IF;

END_CASE;

T_Timeout(IN := Busy, PT := TimeoutLimit);

IF T_Timeout.Q THEN
    AlarmTimeout := TRUE;
    Y_Extend := FALSE;
    Y_Retract := FALSE;
    Busy := FALSE;
    Step := 0;
END_IF;

END_FUNCTION_BLOCK


// ==================================================
// FB_AlarmManager 报警管理函数块
// ==================================================
FUNCTION_BLOCK FB_AlarmManager
VAR_INPUT
    EStopOK        : BOOL;
    DoorOK         : BOOL;
    AirOK          : BOOL;
    ServoOK        : BOOL;
    ScanTimeout    : BOOL;
    SortTimeout    : BOOL;
    Reset          : BOOL;
END_VAR

VAR_OUTPUT
    AlarmActive    : BOOL;
    AlarmCode      : INT;
END_VAR

IF Reset THEN
    AlarmCode := 0;
    AlarmActive := FALSE;
END_IF;

IF NOT EStopOK THEN
    AlarmCode := 1;
    AlarmActive := TRUE;
ELSIF NOT DoorOK THEN
    AlarmCode := 2;
    AlarmActive := TRUE;
ELSIF NOT AirOK THEN
    AlarmCode := 3;
    AlarmActive := TRUE;
ELSIF NOT ServoOK THEN
    AlarmCode := 4;
    AlarmActive := TRUE;
ELSIF ScanTimeout THEN
    AlarmCode := 101;
    AlarmActive := TRUE;
ELSIF SortTimeout THEN
    AlarmCode := 102;
    AlarmActive := TRUE;
END_IF;

END_FUNCTION_BLOCK
"""