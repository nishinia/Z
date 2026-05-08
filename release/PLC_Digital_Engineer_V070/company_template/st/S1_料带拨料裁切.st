//工站运行
rtStart(Clk:=Machine_Data.bStart);
ftStart(Clk:=Machine_Data.bStart);
bRunAble:=NOT Machine_Data.IN.bTip
                   AND Machine_Data.IN.bDoorClosed
       AND Machine_Data.IN.bAutoMode
                   (*AND NOT Station[_StationNum].bStopHome*)
       AND NOT Station[_StationNum].bEstop;
IF rtStart.Q AND bRunAble THEN
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
IF  (Machine_Data.IN.bEmptyDone OR Machine_Data.bStop) AND Station[_StationNum].bRunning THEN
 Station[_StationNum].bStopping:=TRUE;  //循环停止
END_IF;
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
                   IF (Station[_StationNum].bRunning OR 
        Station[_StationNum].bCycleRunning )AND NOT 
        焊接后端尾料模式
       THEN
                    Station[_StationNum].nAutoStep :=10;
                   END_IF;
       
   10:// 预留增加涂油工位物料堆积判断
      Station[_StationNum].nAutoStep :=20;
     
     
             20://
                      Station[_StationNum].nAutoStep :=30;
             30://
                      Station[_StationNum].nAutoStep :=40;
             40://
                        Station[_StationNum].nAutoStep :=50;
 
             50://CY1_Water拨料上下气缸 出
        Cylinder_Data.CY1.Input.bAuto:=TRUE;
                   IF Cylinder_Data.CY1.Output.bWP_Delay  THEN
        MC_Data.AXIS1.Control.bMoveAuto[2]:=TRUE;
                    Station[_StationNum].nAutoStep:=60; 
                   END_IF;
              60://AXIS1Wafer拨料伺服 p2
                   IF MC_Data.AXIS1.Control.bInPosition[2]  THEN
                    Station[_StationNum].nAutoStep:=70;
                   END_IF; 
     70://
                 
                    Station[_StationNum].nAutoStep:=80;

              80://CY1_Water拨料上下气缸 回
        Cylinder_Data.CY1.Input.bAuto:=FALSE;
                   IF  Cylinder_Data.CY1.Output.bHP_Delay THEN
        MC_Data.AXIS1.Control.bMoveAuto[1]:=TRUE;
        
        IF bStep_Wafer[7] THEN
        S1拨料完成:=TRUE;
        END_IF;      
                    Station[_StationNum].nAutoStep:=90;
                   END_IF;
              90://AXIS1拨料伺服 p1,  如果需要裁切要等待裁切完成
                   IF MC_Data.AXIS1.Control.bInPosition[1] THEN
        IF bStep_Wafer[7] THEN
                    Station[_StationNum].nAutoStep:=100;
        ELSIF NOT bStep_Wafer[7] THEN
       Station[_StationNum].nAutoStep:=999;  
        END_IF;
                   END_IF; 
              100://等待各工位完成
                   IF S6裁切完成  THEN
                    Station[_StationNum].nAutoStep:=999;
        S1拨料完成:=FALSE;
                   END_IF; 
       
       
              999://拨料工位END
     IF NOT S6裁切完成 THEN
                    Station[_StationNum].nAutoStep := 0; 
       END_IF;
           END_CASE;
  END_IF;
IF Machine_Data.OUT.bIniting THEN
 Station[_StationNum].nAutoStep:=0;
END_IF;


//拨料Wafer移位
rtWafer移位Up(Clk:=Station[_StationNum].nAutoStep = 10);
bStep_Wafer[0]:=I1_6;
IF rtWafer移位Up.Q THEN
 FOR  nStep_Wafer:=0 TO 50 BY 1 DO
       bStep_Wafer[50-nStep_Wafer]:=bStep_Wafer[49-nStep_Wafer];
 END_FOR;
END_IF;



//Wafer排料计数
IF Wafer尾料BT AND (NOT I0_13) AND rtWafer移位Up.Q THEN
 Wafer排料计数:=Wafer排料计数 + 1;
END_IF;
IF Machine_Data.OUT.bIniting OR (NOT Wafer尾料BT) OR 排料结束 THEN
 Wafer排料计数:=0;
END_IF;
排料结束:=Wafer排料计数>=40;




(************************************************步序延时************************************************)

StepDely[90](IN:= Station[_StationNum].nAutoStep=90,PT:=t#50MS);





(************************************************互锁************************************************)







(************************************************工站报警************************************************)
IF MC_Data.AXIS1.Control.bError THEN//轴报警
  Machine_Alarm.StationAlarm[_StationNum].Alarm[5]:=TRUE;
END_IF;
 
Station[_StationNum].bAlarm:=Cylinder_Data.CY1.Output.bHP_Off OR 
                             Cylinder_Data.CY1.Output.bWP_Off OR           
              Machine_Alarm.StationAlarm[_StationNum].Alarm[1] OR 
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

Station[_StationNum].bTips:=Cylinder_Data.CY1.Output.bAutoTip 
 OR MC_Data.AXIS1.Control.bNotPowerOn;