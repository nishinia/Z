//***********************************************气缸感应器报警*******************************************
// 报警延时
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

//************************************************气缸原动点到位延时********************************************************
// 原点延时
HP_ErrorTime:=NanoSecToTime((REAL_TO_LINT(CylinderData.Input.tHP_Delay*1000)*1000000));
tonHP_Delay(IN:=bHP_Sensor AND NOT bWP_Valve ,
                  PT:=HP_ErrorTime,
                  Q=>CylinderData.Output.bHP_Delay);
// 动点延时
WP_ErrorTime:=NanoSecToTime((REAL_TO_LINT(CylinderData.Input.tWP_Delay*1000)*1000000));
tonWP_Delay(IN:=bWP_Sensor AND bWP_Valve,
                   PT:=WP_ErrorTime,
                   Q=>CylinderData.Output.bWP_Delay);

//*************************************************** 手动操作****************************************************
rtHmi(Clk:=CylinderData.Input.bHmi);
IF rtHmi.Q 
 AND Machine.IN.bEStop AND Machine.IN.bSafety AND Machine.IN.bManualMode AND Machine.IN.bAirOn AND Machine.IN.bManualILC
 AND (
            ((bManual = CylinderData.Input.bAuto)    AND CylinderData.Input.bOnILC)
      OR 
      ((bManual XOR CylinderData.Input.bAuto)AND CylinderData.Input.bOffILC)
     )
THEN
 bManual:=NOT bManual;
END_IF;
// 初始化时复位手动执行
IF CylinderData.Input.bInit OR P_First_Run THEN
 bManual:=FALSE;
  CylinderData.Input.bAuto:=FALSE;
END_IF;

// ********************************************电磁阀手自动输出***********************************************
// 原点阀输出
bHP_Valve:=bManual = CylinderData.Input.bAuto;
// 动点阀输出
bWP_Valve:=bManual XOR CylinderData.Input.bAuto;

CylinderData.Output.BACK:=bManual = CylinderData.Input.bAuto;
CylinderData.Output.GO:=bManual XOR CylinderData.Input.bAuto;
//*********************************************手动中提示************************************************************* 
 CylinderData.Output.bAutoTip:=bManual;
 CylinderData.Input.bInit:=FALSE;