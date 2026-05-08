//按钮
Machine_Data.IN.bAutoMode:=NOT Hmi.bManualModeHmi;
Machine_Data.IN.bManualMode:=Hmi.bManualModeHmi;
(*Machine_Data.bWorkSafety:=Machine_Data.IN.bWorkSafetyButton ;*)
Machine_Data.IN.bManualILC:=Machine_Data.IN.bManualMode AND Machine_Data.IN.bWorkSafetyButton;
Machine_Data.bStart:=Machine_Data.IN.bStartButton OR Hmi.bStartHmi;
Machine_Data.bReset:=Machine_Data.IN.bResetButton OR Hmi.bResetHmi;
Machine_Data.bStop:=Machine_Data.IN.bStopButton OR Hmi.bStopHmi;
Hmi.bStopLightHmi:=NOT Machine_Data.OUT.bRunning;
//不在原点闪烁
Machine_Data.IN.bTip :=Station[1].bTips OR Station[2].bTips OR Station[3].bTips OR Station[4].bTips OR Station[5].bTips OR
                                   Station[6].bTips OR Station[7].bTips OR Station[8].bTips OR Station[9].bTips OR Station[10].bTips;

Hmi.bInitLightHmi:=Machine_Data.IN.bTip  AND Get1sClk();
//设备运行中
Machine_Data.OUT.bRunning:=Station[1].bRunning OR Station[2].bRunning OR Station[3].bRunning OR Station[4].bRunning OR Station[5].bRunning OR
                                          Station[6].bRunning OR Station[7].bRunning ;
//停机灭灯
tStop(In:=Machine_Data.OUT.bStopped,PT:=T#3S);
IF tStop.Q THEN
 bOffAllLights:=TRUE;
ELSIF Machine_Data.bStart THEN
      bOffAllLights:=FALSE;
END_IF;
//启动按钮灯
Machine_Data.OUT.bStartLight:=Machine_Data.OUT.bRunning OR(NOT Machine_Data.IN.bAlarm AND NOT Machine_Data.OUT.bRunning AND NOT Machine_Data.bTips 
                                                       AND (NOT HMI.bManualModeHmi OR Hmi.bCycleModeHmi OR Hmi.bJogModeHmi) AND Get1sClk() ) 
                AND NOT bOffAllLights;
//停止按钮灯
Machine_Data.OUT.bResetLight:=NOT Machine_Data.OUT.bRunning AND NOT bOffAllLights; 
//工安按钮灯
Machine_Data.OUT.bWorkSafetyButtonLight:=Machine_Data.IN.bWorkSafetyButton AND NOT bOffAllLights; 
//三色灯
Machine_Data.OUT.bLampRed:=Machine_Data.IN.bAlarm AND NOT bOffAllLights;
Machine_Data.OUT.bLampYellow:=NOT Machine_Data.IN.bAlarm AND NOT Machine_Data.OUT.bRunning AND NOT bOffAllLights;
Machine_Data.OUT.bLampGreen:=((NOT Machine_Data.IN.bAlarm AND NOT Machine_Data.OUT.bRunning AND Get1sClk())OR
                                                         Machine_Data.OUT.bRunning ) AND NOT bOffAllLights;
rtAlarm(Clk:=Machine_Data.IN.bAlarm);
ftReset(Clk:=Machine_Data.bReset);
IF rtAlarm.Q THEN
 AlarmKeep:=TRUE;
ELSIF ftReset.Q OR Machine_Data.bStop THEN
      AlarmKeep:=FALSE;
END_IF;
tAlarmKeep(In:=AlarmKeep,PT:=T#5S);
Machine_Data.OUT.bLampBuzzer:=AlarmKeep AND NOT tAlarmKeep.Q AND Get1sClk();
//日光灯
Q1_1:=NOT bOffAllLights AND KeepBool.bTurnOnTheLight;
//吸尘器

//消音器