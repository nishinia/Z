StartTime:=NanoSecToTime((REAL_TO_LINT(Setting.启动延时*1000)*1000000));
StopTime:=NanoSecToTime((REAL_TO_LINT(Setting.停止延时*1000)*1000000));
TimeOut:=NanoSecToTime((REAL_TO_LINT(Setting.超时延时*1000)*1000000));
tonStart(IN:=NOT Control.放料感应, PT:=StartTime);
tonStop(IN:=Control.放料感应, PT:=StopTime);
IF tonStart.Q AND 
 Machine.OUT.bRunning AND
 Machine.IN.bEStop AND NOT 
 Control.放料失败 AND 
 Control.放料启动条件
THEN
   MotorOn:=TRUE;
END_IF;   
IF tonStop.Q OR
 NOT Machine.IN.bEStop OR 
 Control.放料失败 OR 
 NOT Control.放料启动条件
THEN
   MotorOn:=FALSE;
END_IF;  
tonTimeOut(IN:=MotorOn, PT:=TimeOut);  
IF tonTimeOut.Q THEN
 Control.放料失败:=TRUE;
ELSIF Machine.IN.bResetButton OR Machine.IN.bResetHmi THEN
      Control.放料失败:=FALSE;
END_IF;
Control.放料马达:=MotorOn OR (Control.手动触发 AND Machine.IN.bEStop);
Control.触发指示灯:=Control.放料马达;
tonMachineStop(IN:=Control.放料启动条件, PT:=T#3S);  
Control.收纸马达:=MotorOn  OR Control.收纸手动触发;//OR NOT tonMachineStop.Q