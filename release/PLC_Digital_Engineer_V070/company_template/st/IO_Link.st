停机触发:=Machine_Data.OUT.bRunning;
CycleEND:= Station[1].nAutoStep=999;
rCycleEnd(Clk:=CycleEND);
IF rCycleEnd.Q THEN
 生产计数N:=生产计数N+1;
t循环时间:=计时; 
 Machine_Data.IN.rCycleTimeRep:=LINT_TO_REAL(TimeToNanoSec(计时)/1000)/10000;
 计时:=T#0ms;
END_IF;
//
计数UP(Clk:=Station[1].nAutoStep=80 AND NOT Machine_Data.IN.bTryRun);
IF bStep_Wafer[31] AND 计数UP.Q AND I6_5 AND I6_6 THEN
 良品计数:=TRUE;
END_IF;
IF bStep_Wafer[31] AND 计数UP.Q AND (not I6_5 OR NOT I6_6) THEN
 不良计数:=TRUE;
END_IF;
IF (Station[1].nAutoStep=20 ) OR Machine_Data.OUT.bIniting THEN
 良品计数:=FALSE;
 不良计数:=FALSE;
END_IF;Machine_Data.IN.rCycleTime:=Machine_Data.IN.rCycleTimeRep/100;
循环计时(In:=Machine_Data.OUT.bRunning AND  Station[1].nAutoStep<999 , PT:=T#9999999S,ET=>计时);

预计产能:=60.0/Machine_Data.IN.rCycleTime;
rMRst(Clk:=Get1minClk());

IF rMRst.Q THEN
 实际产能:=生产计数N;
 生产计数N:=0.0;
END_IF;
//易损件
拨料易损件计数:=(Station[6].nAutoStep>=40 AND Station[6].nAutoStep<=999) ;
SBX200易损件计数:=(Station[2].nAutoStep>=20 AND Station[2].nAutoStep<=30) ;
SBX100易损件计数:=(Station[4].nAutoStep>=20 AND Station[4].nAutoStep<=30) ;

//Input
Machine_Data.IN.bStartButton:=I0_0;       //启动按钮
Machine_Data.IN.bResetButton:=I0_1;   //复位按钮
Machine_Data.IN.bStopButton:=I0_2   ;  //停止按钮
Machine_Data.IN.bWorkSafetyButton:=(I0_3) AND NOT WorkSafetyButtonDelay.Q;  //工安按钮
WorkSafetyButtonDelay(In:=I0_3, PT:=T#10S);
//机器模式按钮
Hmi.bManualModeHmi:=not I0_4;  //机器模式按钮
//缓慢上气阀
Q2_0:=not Machine_Data.OUT.bEStopped AND NOT 加固片尾料模式;
//气压OK，不然气缸不会动
Machine_Data.IN.bAirOn:=  I0_7;   //气压表
//安全门
DoorClosedTON(In:=(not I0_8 OR not I0_9), PT:=T#500ms);
Machine_Data.IN.bDoorClosed:=NOT DoorClosedTON.Q OR 安全门屏蔽BT ; //门开关  
Machine_Data.IN.bSafety:=TRUE;
//安全门锁
Q1_2:=(not Machine_Data.OUT.bRunning AND Machine_Data.IN.bManualMode)  OR 安全门屏蔽BT;
Q1_3:=(not Machine_Data.OUT.bRunning AND Machine_Data.IN.bManualMode) OR 安全门屏蔽BT;
Q1_4:=(not Machine_Data.OUT.bRunning AND Machine_Data.IN.bManualMode) OR 安全门屏蔽BT;
Q1_5:=(not Machine_Data.OUT.bRunning AND Machine_Data.IN.bManualMode) OR 安全门屏蔽BT;
Q3_3:=(not Machine_Data.OUT.bRunning AND Machine_Data.IN.bManualMode) OR 安全门屏蔽BT;
Q3_4:=(not Machine_Data.OUT.bRunning AND Machine_Data.IN.bManualMode) OR 安全门屏蔽BT;
Q3_1:= Machine_Data.OUT.bRunning ;//吸尘
Q3_2:= Machine_Data.OUT.bRunning ;//除静电
Q3_0:= OilManual OR OilManual ;//涂油

//Output
Q0_0:=Machine_Data.OUT.bStartLight;  //启动按钮灯
Q0_1:=Machine_Data.OUT.bResetLight;//复位按钮灯
Q0_2:=Machine_Data.OUT.bStopLight;//停止按钮灯
Q0_3:=Machine_Data.OUT.bWorkSafetyButtonLight;//工安按钮灯
Q0_4:=Machine_Data.OUT.bLampRed;//三色灯 红
Q0_5:=Machine_Data.OUT.bLampYellow;//三色灯 黄
Q0_6:=Machine_Data.OUT.bLampGreen;//三色灯 绿
Q0_7:=Machine_Data.OUT.bLampBuzzer;//三色灯 蜂鸣器
Q1_1:=KeepBool.bTurnOnTheLight;//日光灯_KA1
Q1_0:=KeepBool.bTurnOnTheAirValve;//缓慢上气阀

Machine_Data.bReset:= Machine_Data.IN.bResetButton OR Machine_Data.IN.bResetHmi;
Machine_Data.bStart:=Machine_Data.IN.bStartButton OR Machine_Data.IN.bStartHmi;
Machine_Data.bStop:= Machine_Data.IN.bStopHmi;                                                               //一个循环停止
Machine_Data.bPause:=Machine_Data.IN.bStopButton OR Machine_Data.IN.bPauseHmi ;    //立即停止

tMachineStop(In:=NOT Machine_Data.OUT.bRunning,PT:=T#0.5S);
(*IF tMachineStop.Q THEN
 Q1_2:=TRUE;
 Q1_3:=TRUE;
 Q1_4:=TRUE;
 Q1_5:=TRUE;
ELSE
    Q1_2:=FALSE;
 Q1_3:=FALSE;
 Q1_4:=FALSE;
 Q1_5:=FALSE;
END_IF;*)

//维修模式
To_Machine1[5]:=weixiu_mode;
To_Machine2[5]:=weixiu_mode;
To_Machine3[5]:=weixiu_mode;
To_Machine4[5]:=weixiu_mode;
To_Machine5[5]:=weixiu_mode;
To_Machine6[5]:=weixiu_mode;
To_Machine7[5]:=weixiu_mode;
To_Machine8[5]:=weixiu_mode;

rt维修模式(Clk:=weixiu_mode );
rtFromM1(Clk:=From_Machine1[5]);
rtFromM2(Clk:=From_Machine2[5]);
rtFromM3(Clk:=From_Machine3[5]);
rtFromM4(Clk:=From_Machine4[5]);
rtFromM5(Clk:=From_Machine5[5]);
rtFromM6(Clk:=From_Machine6[5]);
rtFromM7(Clk:=From_Machine7[5]);
rtFromM8(Clk:=From_Machine8[5]);

IF (rt维修模式.Q OR 
  rtFromM1.Q OR 
  rtFromM2.Q OR 
  rtFromM3.Q OR 
  rtFromM4.Q OR 
  rtFromM5.Q OR
  rtFromM6.Q OR
  rtFromM7.Q OR
  rtFromM8.Q) AND 
  NOT All_weixiu_mode 
THEN
 All_weixiu_mode:=TRUE;
ELSIF (rt维修模式.Q OR 
       rtFromM1.Q OR
       rtFromM2.Q OR 
       rtFromM3.Q OR 
       rtFromM4.Q OR 
       rtFromM5.Q OR
       rtFromM6.Q OR
       rtFromM7.Q OR
       rtFromM8.Q) AND
    All_weixiu_mode 
THEN
      All_weixiu_mode:=FALSE;
END_IF;