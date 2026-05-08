//***********************************************气缸感应器报警*******************************************
(*// 报警延时
tonHP(IN:=Machine.IN.bAirOn AND NOT bWP_Valve, PT:=T#3S);
tonWP(IN:=Machine.IN.bAirOn AND  bWP_Valve, PT:=T#3S);
// 先报警复位
IF Machine.bReset THEN
 CylinderData.Output.bHP_Off:=FALSE;
 CylinderData.Output.bWP_Off:=FALSE;
 CylinderData.Output.bHP_On:=FALSE;
 CylinderData.Output.bWP_On:=FALSE;
END_IF;
// 报警输出，Off报警用延时，On报警用感应器，防止感应器抖动时无到位无报警
IF tonHP.Q THEN
 IF NOT bHP_Sensor THEN  //气缸在原点状态3S如果原点感应器不亮原点报警
  CylinderData.Output.bHP_Off:=TRUE;
 END_IF;
 IF bWP_Sensor THEN      //气缸在原点状态3S如果动感应器亮动点报警
  CylinderData.Output.bWP_On:=TRUE;
 END_IF;
END_IF;
IF tonWP.Q THEN
 IF NOT bWP_Sensor THEN
  CylinderData.Output.bWP_Off:=TRUE;
 END_IF;
 IF bHP_Sensor THEN
  CylinderData.Output.bHP_On:=TRUE;
 END_IF;
END_IF;
*)
//************************************************气缸原动点到位延时********************************************************
// 原点延时
HP_ErrorTime:=NanoSecToTime((REAL_TO_LINT(CylinderData.Input.tHP_Delay*1000)*1000000));
tonHP_Delay(IN:=bHP_Valve ,
                  PT:=HP_ErrorTime,
                  Q=>CylinderData.Output.bHP_Delay);
// 动点延时
WP_ErrorTime:=NanoSecToTime((REAL_TO_LINT(CylinderData.Input.tWP_Delay*1000)*1000000));
tonWP_Delay(IN:=bWP_Valve,
                   PT:=WP_ErrorTime,
                   Q=>CylinderData.Output.bWP_Delay);

//*************************************************** 手动操作****************************************************
rtHmi(Clk:=CylinderData.Input.bHmi);//吸气手动
IF rtHmi.Q 
 AND Machine.IN.bEStop AND Machine.IN.bSafety AND Machine.IN.bManualMode AND Machine.IN.bAirOn 
THEN
 BManualBlow:=FALSE;
 CylinderData.Input.bAutoBlow:=FALSE;
 bManual:=NOT bManual;
END_IF;
rtHmi_Copy(Clk:=CylinderData.Input.bHmiBlow);//吹气手动
IF rtHmi_Copy.Q 
 AND Machine.IN.bEStop AND Machine.IN.bSafety AND Machine.IN.bManualMode AND Machine.IN.bAirOn 
THEN
 bManual:=FALSE;
 CylinderData.Input.bAuto:=FALSE;
 BManualBlow:=NOT BManualBlow;
END_IF;
//
IF rtHmi.Q AND CylinderData.Input.bAuto THEN
 CylinderData.Input.bAuto:=FALSE;
END_IF;
// 初始化时复位手动执行
IF CylinderData.Input.bInit OR P_First_Run THEN
 bManual:=FALSE;
 BManualBlow:=FALSE;
  CylinderData.Input.bAuto:=FALSE;
  CylinderData.Input.bAutoBlow:=FALSE;
END_IF;

// ********************************************电磁阀手自动输出***********************************************
// 吸气输出
bHP_Valve:=bManual OR CylinderData.Input.bAuto;
// 吹气输出
bWP_Valve:=BManualBlow OR CylinderData.Input.bAutoBlow;

CylinderData.Output.BACK:=bHP_Valve;
CylinderData.Output.GO:=bWP_Valve;
//*********************************************手动中提示************************************************************* 
 //CylinderData.Output.bAutoTip:=bManual;
 CylinderData.Input.bInit:=FALSE;
 //
 AutoUp(Clk:=CylinderData.Input.bAuto);
 AutoBlow(Clk:=CylinderData.Input.bAuto);
 IF AutoUp.Q OR AutoBlow.Q THEN
  bManual:=FALSE;
  BManualBlow:=FALSE;
 END_IF;