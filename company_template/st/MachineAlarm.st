//设备急停  常闭触点
Machine_Data.IN.bEstop:= I0_5 AND I0_6;
IF NOT Machine_Data.IN.bEstop THEN
    Machine_Data.OUT.bEStopped:=TRUE;
ELSIF Machine_Data.bReset THEN
 Machine_Data.OUT.bEStopped:=FALSE;
END_IF;

//气压报警
IF NOT Machine_Data.IN.bAirOn THEN
   Machine_Alarm.StationAlarm[0].Alarm[1] :=TRUE;
END_IF;

//安全门报警
IF NOT Machine_Data.IN.bDoorClosed THEN
 Machine_Alarm.StationAlarm[0].Alarm[2]:=TRUE; 
END_IF;

//机器不在自动状态
IF Machine_Data.IN.bManualMode AND (NOT Machine_Data.IN.bAlarm AND NOT Machine_Data.OUT.bRunning AND NOT Machine_Data.bTips) AND Machine_Data.bStart THEN
 Machine_Alarm.StationAlarm[0].Alarm[5]:=TRUE; 
END_IF;
//安全门报警
IF NOT I0_8 AND NOT 安全门屏蔽BT THEN
 Machine_Alarm.StationAlarm[0].Alarm[6]:=TRUE; 
END_IF;
IF NOT I0_9 AND NOT 安全门屏蔽BT THEN
 Machine_Alarm.StationAlarm[0].Alarm[7]:=TRUE; 
END_IF;
IF NOT I0_10 AND NOT 安全门屏蔽BT THEN
 Machine_Alarm.StationAlarm[0].Alarm[8]:=TRUE; 
END_IF;
IF NOT I0_11 AND NOT 安全门屏蔽BT THEN
 Machine_Alarm.StationAlarm[0].Alarm[9]:=TRUE; 
END_IF;
IF NOT I2_4 AND NOT 安全门屏蔽BT THEN
 Machine_Alarm.StationAlarm[0].Alarm[10]:=TRUE; 
END_IF;
IF NOT I2_5 AND NOT 安全门屏蔽BT THEN
 Machine_Alarm.StationAlarm[0].Alarm[11]:=TRUE; 
END_IF;

//报警复位
IF Machine_Data.IN.bResetButton OR Machine_Data.IN.bResetHmi THEN
 Machine_Alarm.StationAlarm[0].Alarm:=bInitAlarm;
 Machine_Alarm.StationAlarm[1].Alarm:=bInitAlarm;
 Machine_Alarm.StationAlarm[6].Alarm:=bInitAlarm;
 Machine_Alarm.StationAlarm[7].Alarm:=bInitAlarm;
END_IF;

Machine_Data.IN.bAlarm:=Station[1].bAlarm OR 
             Station[6].bAlarm OR 
             Station[7].bAlarm OR
             Machine_Alarm.StationAlarm[0].Alarm[1] OR
             Machine_Alarm.StationAlarm[0].Alarm[2] OR
             Machine_Alarm.StationAlarm[0].Alarm[3] OR
             Machine_Alarm.StationAlarm[0].Alarm[4] OR
             Machine_Alarm.StationAlarm[0].Alarm[5] OR
             Machine_Alarm.StationAlarm[0].Alarm[6] OR
             Machine_Alarm.StationAlarm[0].Alarm[7] OR
             Machine_Alarm.StationAlarm[0].Alarm[8] OR
             Machine_Alarm.StationAlarm[0].Alarm[9] OR
             Machine_Alarm.StationAlarm[0].Alarm[10] OR
             Machine_Alarm.StationAlarm[0].Alarm[11] OR
             Machine_Alarm.StationAlarm[0].Alarm[12] OR
             Machine_Alarm.StationAlarm[0].Alarm[13] OR
             Machine_Alarm.StationAlarm[0].Alarm[14] OR
             Machine_Alarm.StationAlarm[0].Alarm[15] OR
             Machine_Alarm.StationAlarm[0].Alarm[16] OR
             Machine_Alarm.StationAlarm[0].Alarm[17] OR
             Machine_Alarm.StationAlarm[0].Alarm[18] OR
             Machine_Alarm.StationAlarm[0].Alarm[19] OR
             Machine_Alarm.StationAlarm[0].Alarm[20] ;

            
             
             
//HMI易损件报警延时中转
易损件报警延时(In:= Machine_Alarm.StationAlarm[0].Alarm[15], PT:=T#5S);
IF 易损件报警延时.Q AND NOT Machine_Data.IN.bTryRun THEN
 Machine_Alarm.StationAlarm[0].Alarm[16]:=TRUE; 
END_IF;