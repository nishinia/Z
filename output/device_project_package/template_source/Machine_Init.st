// 设备初始化条件
IF P_First_Run OR Machine_Data.OUT.bEStopped OR Machine_Data.OUT.bInitTimeout THEN
 Machine_Data.IN.bInitDone:=FALSE;
END_IF;
bInitAble:=Machine_Data.IN.bEstop AND Machine_Data.IN.bSafety AND NOT ( Machine_Alarm.StationAlarm[2].Alarm[1] OR
                       Machine_Alarm.StationAlarm[2].Alarm[2] OR
                       Machine_Alarm.StationAlarm[2].Alarm[3] OR
                       Machine_Alarm.StationAlarm[2].Alarm[5] OR
             Station[3].bAlarm OR 
     //        Station[4].bAlarm OR 
             Machine_Alarm.StationAlarm[4].Alarm[1] OR
                       Machine_Alarm.StationAlarm[4].Alarm[2] OR
                       Machine_Alarm.StationAlarm[4].Alarm[3] OR
                       Machine_Alarm.StationAlarm[4].Alarm[5] OR
                                           Station[5].bAlarm OR 
             Station[6].bAlarm OR 
             Station[7].bAlarm OR 
             Station[8].bAlarm OR 
             Station[9].bAlarm OR 
             Station[10].bAlarm OR
             Machine_Alarm.StationAlarm[0].Alarm[1] OR
             Machine_Alarm.StationAlarm[0].Alarm[2] OR
             Machine_Alarm.StationAlarm[0].Alarm[3] OR
             Machine_Alarm.StationAlarm[0].Alarm[14]) AND NOT Machine_Data.OUT.bInitTimeout AND Machine_Data.IN.bManualILC;
// 初始化上升沿，弹出初始化确认对话框
rtInit(CLK:=Machine_Data.IN.bInit );
IF rtInit.Q AND bInitAble AND NOT Machine_Data.OUT.bIniting THEN
  Machine_Data.OUT.bIniting :=TRUE; 
END_IF;
//系统复位前请先拉起棘轮
IF rtInit.Q AND bInitAble AND NOT Machine_Data.OUT.bIniting THEN
 Machine_Alarm.StationAlarm[0].Alarm[11]:=TRUE; 
END_IF;
// 初始化超时
tonInitTimeout(IN:=Machine_Data.OUT.bIniting,PT:=T#50S);
IF Machine_Data.bReset THEN
 Machine_Data.OUT.bInitTimeout:=FALSE;
END_IF;
IF tonInitTimeout.Q THEN
 Machine_Data.OUT.bInitTimeout:=TRUE;
 Machine_Data.OUT.bIniting:=FALSE;
 nInitStep := 0;
END_IF;
//自动运行
IF  Machine_Data.OUT.bIniting  THEN
     CASE nInitStep OF    
               00://等待系统复位
                    IF InitTON[0].Q AND Machine_Data.OUT.bIniting THEN
      S1拨料完成:=FALSE;
      S6裁切完成:=FALSE;
                        nInitStep := 10;
                    END_IF;
               10://上下气缸回
         Station[1].bCycleRunning:=FALSE;
      Station[6].bCycleRunning:=FALSE;
      Station[7].bCycleRunning:=FALSE;
         Machine_Data.IN.bInitDone:=FALSE;
                   Cylinder_Data.CY1.Input.bInit:=TRUE;
       MC_Data.AXIS1.Control.bPowerOnInit:=TRUE;
       MC_Data.AXIS2.Control.bPowerOnInit:=TRUE;
       MC_Data.AXIS3.Control.bPowerOnInit:=TRUE;
                IF InitTON[1].Q AND Cylinder_Data.CY1.Output.bHP_Delay THEN
                       nInitStep := 50;
                  END_IF; 
    50:   
      IF InitTON[5].Q THEN
       MC_Data.AXIS1.Control.bMoveAuto[1]:=TRUE;
        MC_Data.AXIS2.Control.bMoveAuto[1]:=TRUE;
         MC_Data.AXIS3.Control.bMoveAuto[1]:=TRUE;
       nInitStep := 60;
      END_IF;
     60://
       IF InitTON[6].Q AND
     MC_Data.AXIS1.Control.bInPosition[1] AND MC_Data.AXIS2.Control.bInPosition[1] AND MC_Data.AXIS3.Control.bInPosition[1]THEN  
                    nInitStep := 70;
    END_IF;
               70://
                    IF InitTON[7].Q THEN
                        nInitStep := 80;
                    END_IF; 
               80:// 
                   IF InitTON[8].Q THEN      
                        nInitStep := 90;
                    END_IF;      
               90://
        IF InitTON[9].Q THEN
                      nInitStep := 100;
     END_IF;
               100://初始化END
          Machine_Data.IN.bInitDone:=TRUE;
          Machine_Data.OUT.bIniting:=FALSE;
                   nInitStep := 999;
               999:
                   nInitStep := 0;
     END_CASE;
END_IF;
InitTON[0](In:=nInitStep=0, PT:=T#500ms);
InitTON[1](In:=nInitStep=10, PT:=T#500ms);
InitTON[2](In:=nInitStep=20, PT:=T#500ms);
InitTON[3](In:=nInitStep=30 ,PT:=T#500ms);
InitTON[4](In:=nInitStep=40, PT:=T#500ms);
InitTON[5](In:=nInitStep=50, PT:=T#500ms);
InitTON[6](In:=nInitStep=60, PT:=T#500ms);
InitTON[7](In:=nInitStep=70, PT:=T#500ms);
InitTON[8](In:=nInitStep=80, PT:=T#500ms);
InitTON[9](In:=nInitStep=90, PT:=T#500ms);
InitTON[10](In:=nInitStep=12, PT:=T#500ms);