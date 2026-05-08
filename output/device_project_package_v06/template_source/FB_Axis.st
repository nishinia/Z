(********************************************************轴使能********************************************************)
//第一次上电  原点标志复位
IF P_First_Run THEN
 Data.Control.bHomeKeep:=FALSE;
END_IF;
//power on  按钮上升沿
rtPowerHmi(CLK:=Data.Control.bPowerOnHmi);
//急停按钮按下
IF  Machine.IN.bEStop THEN
    IF (rtPowerHmi.Q AND Machine.IN.bManualMode) THEN
  IF NOT bPowerAuto THEN
    bPowerManual:=NOT bPowerManual;
  ELSIF bPowerAuto THEN
   bPowerAuto:=FALSE;     
  END_IF;
 END_IF;
//需要再外部程序给 Data.Control.bPowerOnInit=1
 IF Data.Control.bPowerOnInit   THEN   
  bPowerAuto:=TRUE;
  bPowerManual:=FALSE;
  Data.Control.iPosNumber:=0;
 END_IF;
//如果急停按下
ELSE
          bPowerManual:=FALSE;
    bPowerAuto:=FALSE;

END_IF;
//使能
MC_Power1(Axis:=Basic_Axis, 
                    Enable:=(bPowerManual OR bPowerAuto) AND NOT Data.Control.bError ,
                    Status=>Data.Control.bPowerOn);


//轴运行条件
bRunable:=Machine.IN.bEStop AND Machine.IN.bSafety AND Data.Control.bMoveILC AND 
  Basic_Axis.Status.Standstill AND NOT Basic_Axis.DrvStatus.DrvAlarm AND Basic_Axis.DrvStatus.Ready;
(****************************JOG****************************)
rtJogForward (Clk:=Data.Control.bJogForwardHmi);
rtJogBackwards(Clk:=Data.Control.bJogBackwardsHmi);
bJogForward:=bRunable AND Data.Control.bJogForwardHmi  AND Machine.IN.bManualMode AND Machine.IN.bManualILC;
bJogBackwards:=bRunable AND Data.Control.bJogBackwardsHmi AND Machine.IN.bManualMode AND Machine.IN.bManualILC;
(*IF bJogForward THEN
 rTargetPosition:=Data.Setting.rJogPosition;
ELSE
 rTargetPosition:=-Data.Setting.rJogPosition;
END_IF;*)


MC_MoveJog1(Axis:=Basic_Axis,
                       PositiveEnable:=bJogForward,
        NegativeEnable:=bJogBackwards,
        Velocity:=Data.Setting.rJogVelocity,
        Acceleration:=Data.Setting.rJogPosition,
        Deceleration:=Data.Setting.rJogDeceleration);


(****************************Home****************************)
rtHomeHmi(CLK:=Data.Control.bHomeHmi);
bHomeManual:=rtHomeHmi.Q AND Machine.IN.bManualMode;
//手动回零   自动回零两个条件
bHomeExecute:=bRunable AND ((bHomeManual AND Machine.IN.bManualILC) OR Data.Control.bHomeAuto);
MC_Home1(Axis:=Basic_Axis,
                    Execute:=bHomeExecute);
//IF MC_Home1.Done THEN
 Data.Control.bHomeKeep:=TRUE;
//END_IF;
IF MC_Home1.Done THEN
 Data.Control.bHomeDone:=TRUE;
ELSIF bHomeExecute  THEN
 Data.Control.bHomeDone:=FALSE; 
END_IF; 


(****************************MoveAbsolute****************************)
//定位位置
FOR nMoveNum:= 0 TO 20 BY 1 DO
  //自动手动在一起
 IF Data.Control.bMoveAuto[nMoveNum] OR (Machine.IN.bManualMode AND Machine.IN.bManualILC AND Data.Control.bMoveManual[nMoveNum] AND Data.Control.bHomeKeep) THEN
  rTargetPosition:= Data.Setting.rMovePosition[nMoveNum];
  nMoveNum:=0;
  bMoveExecute:=1;
  EXIT;
 ELSE 
  bMoveExecute:=0;
 END_IF;
END_FOR;
//定位速度
IF Machine.IN.bManualMode THEN
 rTargetVelocity:= Data.Setting.rAutoVelocity;
ELSE
    rTargetVelocity:= Data.Setting.rAutoVelocity;
END_IF;

(********************************************************绝对定位********************************************************)
rtManualExecute(CLK:=bMoveExecute);
bAbsoluteExecute:=bRunable  AND bMoveExecute AND Data.Setting.bMoveMode=0;
MC_MoveAbsolute1(Axis:=Basic_Axis, 
                               Execute:=bAbsoluteExecute, 
          Position:=rTargetPosition, 
          Velocity:=rTargetVelocity, 
          Acceleration:=Data.Setting.rMoveAcceleration, 
          Deceleration:=Data.Setting.rMoveDeceleration);
(********************************************************相对定位********************************************************)
bRelativeExecute:=bRunable  AND bMoveExecute AND Data.Setting.bMoveMode=1;
MC_MoveRelative1(Axis:=Basic_Axis, 
                               Execute:=bRelativeExecute, 
          Distance:=rTargetPosition, 
          Velocity:=rTargetVelocity, 
          Acceleration:=Data.Setting.rMoveAcceleration, 
          Deceleration:=Data.Setting.rMoveDeceleration);
(********************************************************到位指示灯********************************************************)

FOR nPositionNum:= 0 TO 20 BY 1 DO
 tonMoveInPos[nPositionNum](
                                                 In:=Data.Control.rActPos+0.03 >= Data.Setting.rMovePosition[nPositionNum] 
                                    AND Data.Setting.rMovePosition[nPositionNum] >= Data.Control.rActPos-0.03
                                    AND Data.Control.bHomeKeep, 
                                    PT:=NanoSecToTime(REAL_TO_LINT(Data.Setting.tMoveInPos[nPositionNum]*1000)*1000000),              
                                    Q=>Data.Control.bInPosition[nPositionNum]); 
END_FOR;

FOR TeachNum:= 0 TO 20 BY 1 DO
 IF Data.Control.bTeachHmi[TeachNum] THEN
    Data.Setting.rMovePosition[TeachNum]:=LREAL_TO_REAL(In:=Basic_Axis.Cmd.Pos) ;
 END_IF;
END_FOR;


(********************************************************错误清除********************************************************)
MC_Reset1(Axis:=Basic_Axis, 
                   Execute:=Machine.bReset OR Data.Control.bAlarmReset);
(********************************************************轴状态********************************************************)
Data.Control.rActPos:=LREAL_TO_REAL(In:=Basic_Axis.Cmd.Pos);
//Data.Control.rActPos:=Basic_Axis.Cmd.Pos;//当前位置
Data.Control.bBusy:=Basic_Axis.Status.Discrete ;//运行中
IF Basic_Axis.DrvStatus.DrvAlarm OR Basic_Axis.MFaultLvl.Code<>0 THEN
 Data.Control.bError:=TRUE;
END_IF;
Data.Control.bWarning:=Basic_Axis.DrvStatus.DrvWarning;//警告
Data.Control.nAxisErrorID:=Basic_Axis.MFaultLvl.Code;//故障ID
//AxisData.Status.nServoErrorID:=;//警告ID

bReady:=Basic_Axis.Status.Standstill AND NOT Basic_Axis.DrvStatus.DrvAlarm AND Basic_Axis.DrvStatus.Ready;
(********************************************************自动提示********************************************************)
tAxisBusy(IN:= Basic_Axis.Details.Idle,PT:=T#0.5S);
FOR Data.Control.iPosIndex:=1 TO 20 DO
        IF NOT Basic_Axis.Details.Idle AND Data.Control.bMoveAuto[Data.Control.iPosIndex] THEN
         Data.Control.iPosNumber := Data.Control.iPosIndex;
   Data.Control.bMoveAuto[Data.Control.iPosIndex]:=FALSE;
        END_IF;
END_FOR;

IF NOT Machine.OUT.bRunning  AND tAxisBusy.Q THEN
    FOR Data.Control.iPosIndex:=1 TO 20 DO
        IF  Data.Control.iPosNumber = Data.Control.iPosIndex AND NOT Data.Control.bInPosition[Data.Control.iPosIndex] THEN
        Data.Control.bAutoTips[Data.Control.iPosIndex] := TRUE;//轴应在自动位置提示
     ELSE
      Data.Control.bAutoTips[Data.Control.iPosIndex] := FALSE;
       END_IF;
   END_FOR;
END_IF;
(********************************************************手动提示********************************************************)
//未使能提示
IF Machine.bReset THEN
    Data.Control.bNotPowerOn := FALSE;
 Data.Control.bError:=FALSE;
END_IF;
FOR Data.Control.iMoveIndex:=1 TO 20 DO
    rMoveAxis_HMI(CLK:=Data.Control.bMoveManual[Data.Control.iMoveIndex]);
    IF rMoveAxis_HMI.Q AND Machine.IN.bManualMode AND Machine.IN.bSafety AND NOT Data.Control.bPowerOn THEN
     Data.Control.bNotPowerOn:= TRUE;
    END_IF;
END_FOR;
//先复位
FOR Data.Control.iMoveIndex:=1 TO 20 DO 
 IF Machine.bReset THEN 
        Data.Control.bManualTips[Data.Control.iMoveIndex] := FALSE;
 END_IF;
END_FOR;
//手动提示
FOR Data.Control.iMoveIndex:=1 TO 20 DO
 rMoveAxis_HMI(CLK:=Data.Control.bMoveManual[Data.Control.iMoveIndex]);
    IF Machine.IN.bManualMode AND rMoveAxis_HMI.Q AND Data.Control.bPowerOn AND NOT Data.Control.bMoveILC AND NOT Data.Control.bBusy THEN
     Data.Control.bManualTips[Data.Control.iMoveIndex] := TRUE;
    END_IF;
END_FOR;

//***********************************************自动指令复位********************************************
  (*Data.Control.bMoveAuto:=bMoveRst;*)
  Data.Control.bHomeAuto:=FALSE;
  Data.Control.bPowerOnInit :=FALSE;