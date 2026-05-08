AXIS1FB(Basic_Axis:=Axis1拨料伺服, Data:=MC_Data.AXIS1, Machine:=Machine_Data);
               MC_Data.AXIS1.Control.bMoveILC:=TRUE;      
AXIS2FB(Basic_Axis:=Axis2裁切伺服, Data:=MC_Data.AXIS2, Machine:=Machine_Data);
               MC_Data.AXIS2.Control.bMoveILC:=TRUE;                  
AXIS3FB(Basic_Axis:=Axis3涂油伺服, Data:=MC_Data.AXIS3, Machine:=Machine_Data);
               MC_Data.AXIS3.Control.bMoveILC:=TRUE;      
      MC_Data.AXIS3.Setting.bMoveMode:=1;
      
     
      
(*//单独送一次
IF MC_Data.AXIS3.Control.bMoveManual[2] AND Machine_Data.IN.bManualMode THEN
 MC_Data.AXIS3.Setting.bMoveMode:=1;
 IF MC_Data.AXIS3.Control.bInPosition[4] THEN
  MC_Data.AXIS3.Setting.rMovePosition[3]:=MC_Data.AXIS3.Setting.rMovePosition[4];
 END_IF;
END_IF;
AXIS3FB(Basic_Axis:=Axis3涂油伺服, Data:=MC_Data.AXIS3, Machine:=Machine_Data);
               MC_Data.AXIS3.Control.bMoveILC:=TRUE ;
//回原点计算
Axis3除数:=MC_Data.AXIS3.Control.rActPos/MC_Data.AXIS3.Setting.rMovePosition[2];
Axis3除数1:=REAL_TO_INT(In:=Axis3除数);
IF MC_Data.AXIS3.Control.rActPos>=350 THEN
 MC_Data.AXIS3.Setting.rMovePosition[4]:=350;
ELSIF MC_Data.AXIS3.Control.rActPos<=0 THEN
 MC_Data.AXIS3.Setting.rMovePosition[4]:=0;
ELSE
 MC_Data.AXIS3.Setting.rMovePosition[4]:=(Axis3除数1)*MC_Data.AXIS3.Setting.rMovePosition[2]+MC_Data.AXIS3.Setting.rMovePosition[1];
END_IF;      
      *)
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
(*AXIS2FB(Basic_Axis:=AXIS2SBX200裁切伺服, Data:=MC_Data.AXIS2, Machine:=Machine_Data);
               MC_Data.AXIS2.Control.bMoveILC:=NOT MC_Data.AXIS6.Control.bInPosition[2];

AXIS4FB(Basic_Axis:=AXIS4SBX200分Pitch伺服, Data:=MC_Data.AXIS4, Machine:=Machine_Data);
               MC_Data.AXIS4.Control.bMoveILC:=TRUE;
AXIS5FB(Basic_Axis:=AXIS5SBX200搬运Z伺服, Data:=MC_Data.AXIS5, Machine:=Machine_Data);
               MC_Data.AXIS5.Control.bMoveILC:=MC_Data.AXIS6.Control.bInPosition[1];
      MC_Data.AXIS5.Control.bProtect[1]:=MC_Data.AXIS6.Control.bInPosition[1] OR MC_Data.AXIS6.Control.bInPosition[3];
      MC_Data.AXIS5.Control.bProtect[2]:=MC_Data.AXIS6.Control.bInPosition[1] OR MC_Data.AXIS6.Control.bInPosition[2];
      MC_Data.AXIS5.Control.bProtect[3]:=MC_Data.AXIS6.Control.bInPosition[1] OR MC_Data.AXIS6.Control.bInPosition[2];
      MC_Data.AXIS5.Control.bProtect[4]:=MC_Data.AXIS6.Control.bInPosition[1] OR MC_Data.AXIS6.Control.bInPosition[3];
AXIS6FB(Basic_Axis:=AXIS6SBX200搬运Y伺服, Data:=MC_Data.AXIS6, Machine:=Machine_Data);
               MC_Data.AXIS6.Control.bMoveILC:=MC_Data.AXIS5.Control.bInPosition[1] AND MC_Data.AXIS2.Control.bInPosition[1];
      MC_Data.AXIS6.Control.bProtect[1]:=MC_Data.AXIS5.Control.bInPosition[1] OR (MC_Data.AXIS6.Control.bInPosition[2] AND MC_Data.AXIS5.Control.bInPosition[2])
         OR (MC_Data.AXIS6.Control.bInPosition[2] AND MC_Data.AXIS5.Control.bInPosition[3]);
      MC_Data.AXIS6.Control.bProtect[2]:=Cylinder_Data.CY15.Output.bHP_Delay and MC_Data.AXIS2.Control.bInPosition[1] and (MC_Data.AXIS5.Control.bInPosition[2] OR MC_Data.AXIS5.Control.bInPosition[3]);
      MC_Data.AXIS6.Control.bProtect[3]:=MC_Data.AXIS5.Control.bInPosition[1];
AXIS7FB(Basic_Axis:=AXIS7SBX100裁切伺服, Data:=MC_Data.AXIS7, Machine:=Machine_Data);      
               MC_Data.AXIS7.Control.bMoveILC:=NOT MC_Data.AXIS11.Control.bInPosition[2];
//单独送一次
IF MC_Data.AXIS8.Control.bMoveManual[2] AND Machine_Data.IN.bManualMode THEN
 MC_Data.AXIS8.Setting.bMoveMode:=1;
 IF MC_Data.AXIS8.Control.bInPosition[4] THEN
  MC_Data.AXIS8.Setting.rMovePosition[3]:=MC_Data.AXIS8.Setting.rMovePosition[4];
 END_IF;
END_IF;
AXIS8FB(Basic_Axis:=AXIS8SBX100送料伺服, Data:=MC_Data.AXIS8, Machine:=Machine_Data);      
               MC_Data.AXIS8.Control.bMoveILC:=MC_Data.AXIS7.Control.bInPosition[1] ;
//回原点计算
Axis8除数:=MC_Data.AXIS8.Control.rActPos/MC_Data.AXIS8.Setting.rMovePosition[2];
Axis8除数1:=REAL_TO_INT(In:=Axis8除数);
IF MC_Data.AXIS8.Control.rActPos>=350 THEN
 MC_Data.AXIS8.Setting.rMovePosition[4]:=350;
ELSIF MC_Data.AXIS8.Control.rActPos<=0 THEN
 MC_Data.AXIS8.Setting.rMovePosition[4]:=0;
ELSE
 MC_Data.AXIS8.Setting.rMovePosition[4]:=(Axis3除数1)*MC_Data.AXIS8.Setting.rMovePosition[2]+MC_Data.AXIS8.Setting.rMovePosition[1];
END_IF;
(*IF MC_Data.AXIS8.Control.rActPos>=350 THEN
 MC_Data.AXIS8.Setting.rMovePosition[4]:=350;
ELSIF MC_Data.AXIS8.Control.rActPos<=-350 THEN
 MC_Data.AXIS8.Setting.rMovePosition[4]:=-350;
ELSE
 MC_Data.AXIS8.Setting.rMovePosition[4]:=(Axis8除数1)*MC_Data.AXIS8.Setting.rMovePosition[2]+MC_Data.AXIS8.Setting.rMovePosition[1];
END_IF;*)
(*AXIS9FB(Basic_Axis:=AXIS9SBX100分Pitch伺服, Data:=MC_Data.AXIS9, Machine:=Machine_Data);      
               MC_Data.AXIS9.Control.bMoveILC:=TRUE;
AXIS10FB(Basic_Axis:=AXIS10SBX100搬运Z伺服, Data:=MC_Data.AXIS10, Machine:=Machine_Data);      
               MC_Data.AXIS10.Control.bMoveILC:=MC_Data.AXIS11.Control.bInPosition[1];
      MC_Data.AXIS10.Control.bProtect[1]:=MC_Data.AXIS11.Control.bInPosition[1] OR MC_Data.AXIS11.Control.bInPosition[3];
      MC_Data.AXIS10.Control.bProtect[2]:=MC_Data.AXIS11.Control.bInPosition[1] OR MC_Data.AXIS11.Control.bInPosition[2];
      MC_Data.AXIS10.Control.bProtect[3]:=MC_Data.AXIS11.Control.bInPosition[1] OR MC_Data.AXIS11.Control.bInPosition[2];
      MC_Data.AXIS10.Control.bProtect[4]:=MC_Data.AXIS11.Control.bInPosition[1] OR MC_Data.AXIS11.Control.bInPosition[3];
AXIS11FB(Basic_Axis:=AXIS11SBX100搬运Y伺服, Data:=MC_Data.AXIS11, Machine:=Machine_Data);      
               MC_Data.AXIS11.Control.bMoveILC:=MC_Data.AXIS10.Control.bInPosition[1] AND MC_Data.AXIS7.Control.bInPosition[1];
      MC_Data.AXIS11.Control.bProtect[1]:=MC_Data.AXIS10.Control.bInPosition[1] OR (MC_Data.AXIS11.Control.bInPosition[2] AND MC_Data.AXIS10.Control.bInPosition[2])
         OR (MC_Data.AXIS11.Control.bInPosition[2] AND MC_Data.AXIS10.Control.bInPosition[3]);
      MC_Data.AXIS11.Control.bProtect[2]:=Cylinder_Data.CY18.Output.bHP_Delay and MC_Data.AXIS7.Control.bInPosition[1] and (MC_Data.AXIS10.Control.bInPosition[2] OR MC_Data.AXIS10.Control.bInPosition[3]);
      MC_Data.AXIS11.Control.bProtect[3]:=MC_Data.AXIS10.Control.bInPosition[1];*)
//Wafer放料马达控制
Motor1Control.放料感应:=I2_1;//裁切料带有无感应
Motor1Control.手动触发:= I2_0;
Motor1Control.收纸手动触发:=Machine_Data.OUT.bRunning OR Motor1Control.放料马达;
Motor1Control.放料启动条件:=NOT Machine_Data.IN.bTryRun AND NOT Wafer尾料BT;
Q2_0:=Motor1Control.放料马达;
Q2_1:=Motor1Control.收纸马达;
Q2_4:=Motor1Control.触发指示灯;
motor1(Control:=Motor1Control, Setting:=Motor1Setting, Machine:=Machine_Data);
//SB放料马达控制
(*Motor2Control.放料感应:=I10_4;//裁切料带有无感应
Motor2Control.手动触发:= I10_1 ;
Motor2Control.收纸手动触发:=Machine_Data.OUT.bRunning OR Motor2Control.放料马达;
Motor2Control.放料启动条件:=NOT Machine_Data.IN.bTryRun AND NOT SBX200尾料BT;
Q4_1:=Motor2Control.放料马达;
Q4_5:=Motor2Control.收纸马达;
Q5_1:=Motor2Control.触发指示灯;
motor2(Control:=Motor2Control, Setting:=Motor2Setting, Machine:=Machine_Data);*)
(*//SBX100放料马达控制
Motor3Control.放料感应:=I10_5;//裁切料带有无感应
Motor3Control.手动触发:= I10_2 ;
Motor3Control.收纸手动触发:=Machine_Data.OUT.bRunning OR Motor3Control.放料马达;
Motor3Control.放料启动条件:=NOT Machine_Data.IN.bTryRun AND NOT SBX100尾料BT;
Q4_2:=Motor3Control.放料马达;
Q4_6:=Motor3Control.收纸马达;
Q5_2:=Motor3Control.触发指示灯;
motor3(Control:=Motor3Control, Setting:=Motor3Setting, Machine:=Machine_Data);*)
//收料马达控制
Motor4Control.放料感应:=NOT I2_3;//裁切料带有无感应
Motor4Control.手动触发:= I2_2 ;
Motor4Control.收纸手动触发:=Machine_Data.OUT.bRunning OR Motor4Control.放料马达;
Motor4Control.放料启动条件:=NOT Machine_Data.IN.bTryRun AND NOT 收料尾料BT ;
Q2_2:=Motor4Control.放料马达;
Q2_3:=Motor4Control.收纸马达;
Q2_5:=Motor4Control.触发指示灯;
motor4(Control:=Motor4Control, Setting:=Motor4Setting, Machine:=Machine_Data);