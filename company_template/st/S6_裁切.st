//工站运行
rtStart(Clk:=Machine_Data.bStart);
ftStart(Clk:=Machine_Data.bStart);
bRunAble:=NOT Machine_Data.IN.bTip
                   AND Machine_Data.IN.bDoorClosed
       AND Machine_Data.IN.bAutoMode
                   (*AND NOT Station[_StationNum].bStopHome*)
       AND NOT Station[_StationNum].bEstop;
IF rtStart.Q AND bRunAble AND NOT LasereEnavailable THEN
 Station[_StationNum].bRunning:=TRUE;
 停机触发:=TRUE;
ELSIF NOT bRunAble THEN
    Station[_StationNum].bRunning:=FALSE;
 停机触发:=FALSE;
END_IF;

//循环模式一个循环停止
IF Station[_StationNum].bRunning AND Hmi.bCycleModeHmi AND Station[_StationNum].nAutoStep= 999 THEN
 Station[_StationNum].bRunning:=FALSE;
END_IF;

//点动模式停止
IF Hmi.bJogModeHmi AND ftStart.Q THEN
    Station[_StationNum].bRunning:=FALSE; 
END_IF;

//连循环模式 一个循环停止
IF (Station[_StationNum].bRunning AND Hmi.bCycleModeHmi AND Station[_StationNum].nAutoStep= 999) OR nAutoStep0.Q OR Machine_Data.bStop THEN
 Station[_StationNum].bStopping:=TRUE;  //循环停止
END_IF;
nAutoStep0(In:=Station[_StationNum].bRunning AND Hmi.bCycleModeHmi AND Station[_StationNum].nAutoStep= 0, PT:=T#3S);
IF Station[_StationNum].bStopping AND Station[_StationNum].bStopHome THEN
   Station[_StationNum].bRunning:=FALSE;
      Station[_StationNum].bStopping:=FALSE;
END_IF;
//暂停
IF  Station[_StationNum].bEstop OR Machine_Data.bPause THEN
      Station[_StationNum].bRunning:=FALSE;
   Station[_StationNum].bStopping:=FALSE;
END_IF;
//原点和超时停止
tStopping(In:=Station[_StationNum].bStopping,PT:=t#6S);
Station[_StationNum].bStopHome:=Station[_StationNum].nAutoStep= 999 OR tStopping.Q;
//立即停止
Station[_StationNum].bEstop:=All_weixiu_mode OR Machine_Data.IN.bAlarm OR Machine_Data.OUT.bEStopped OR (ftStart.Q AND Hmi.bJogModeHmi) 
                              OR (Station[_StationNum].nAutoStep= 999 AND Hmi.bCycleModeHmi);
//工站单循环
rtCycleRun(Clk:=Station[_StationNum].bCycleRun OR Station[_StationNum].bJogRun);
ftJogStop(Clk:=Station[_StationNum].bJogRun);
IF rtCycleRun.Q AND NOT Station[_StationNum].bTips AND NOT Station[_StationNum].bAlarm AND Machine_Data.IN.bManualMode  THEN
 Station[_StationNum].bCycleRunning:=TRUE;
ELSIF Station[_StationNum].bTips OR Station[_StationNum].bAlarm OR Station[_StationNum].bStopHome OR ftJogStop.Q THEN
      Station[_StationNum].bCycleRunning:=FALSE;
END_IF;
//工站自动运行
IF Station[_StationNum].nAutoStep= 999 THEN
 Station[_StationNum].nAutoStep:= 0;
END_IF;
IF Station[_StationNum].bRunning OR Station[_StationNum].bCycleRunning  THEN
    CASE Station[_StationNum].nAutoStep OF     
              00://Home Step
                   IF Station[_StationNum].bRunning OR Station[_StationNum].bCycleRunning
       THEN
                    Station[_StationNum].nAutoStep :=10;
                   END_IF;
               10://等待可裁切
                   IF  ( S1拨料完成   AND I0_12 AND I0_13 AND I0_14)    OR Station[_StationNum].bCycleRunning THEN
                    Station[_StationNum].nAutoStep:=20;
                   END_IF;
              20://
                    Station[_StationNum].nAutoStep:=30;
              30://去裁切位P2 
           MC_Data.AXIS2.Control.bMoveAuto[2]:=TRUE;
                    Station[_StationNum].nAutoStep:=40;

              40://等待到裁切位
                  IF  MC_Data.AXIS1.Control.bInPosition[2]  THEN
                    Station[_StationNum].nAutoStep:=50;
      END_IF;
              50://          
        Station[_StationNum].nAutoStep:=60;    
             60:////回待机位 P1  
                       MC_Data.AXIS2.Control.bMoveAuto[1]:=TRUE;
                    Station[_StationNum].nAutoStep:=70;
             70://
        IF MC_Data.AXIS1.Control.bInPosition[1]  THEN  
            S6裁切完成:=TRUE;
                    Station[_StationNum].nAutoStep:=80;
     END_IF;
     
    80:// 
     IF NOT S1拨料完成 THEN
      S6裁切完成:=FALSE;
        Station[_StationNum].nAutoStep:=90;
     END_IF;
    90:// 
     Station[_StationNum].nAutoStep:=999;
             999://
         Station[_StationNum].bCycleRunning:=FALSE;
                    Station[_StationNum].nAutoStep := 0; 
         END_CASE;
END_IF;
IF Machine_Data.OUT.bIniting THEN
 Station[_StationNum].nAutoStep:=0;
END_IF;

(************************************************步序延时************************************************)

StepDely[90](IN:= Station[_StationNum].nAutoStep=90,PT:=t#50MS);






(************************************************互锁************************************************)









(************************************************工站报警************************************************)
IF MC_Data.AXIS2.Control.bError THEN//轴报警
  Machine_Alarm.StationAlarm[_StationNum].Alarm[5]:=TRUE;
END_IF;
Station[_StationNum].bAlarm:=Machine_Alarm.StationAlarm[_StationNum].Alarm[1] OR 
              Machine_Alarm.StationAlarm[_StationNum].Alarm[2] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[3] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[4] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[5] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[6] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[7] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[8] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[9] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[10] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[11] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[12] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[13] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[14] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[15] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[16] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[17] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[18] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[19] OR
              Machine_Alarm.StationAlarm[_StationNum].Alarm[20] ;
(************************************************工站提示************************************************)
Machine_Alarm.StationWarning[_StationNum].Warning[1] :=Station[_StationNum].bRunning AND
                                                                                                Station[_StationNum].nAutoStep=0 AND
                                          NOT From_Machine5[1] ; 
Station[_StationNum].bTips:= MC_Data.AXIS2.Control.bNotPowerOn;