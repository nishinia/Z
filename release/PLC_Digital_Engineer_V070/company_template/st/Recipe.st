//当前料号名称
HMIRecipe.CurrentPNName:=PNName[HMIRecipe.CurrentID];
//
ButtonDelay(In:=HMIRecipe.LoadDone OR HMIRecipe.SaveDone, PT:=T#3S);
IF ButtonDelay.Q THEN
 HMIRecipe.LoadDone:=FALSE;
 HMIRecipe.SaveDone:=FALSE;
END_IF;
//配方参数————>界面(下载)
rtRecipe1(Clk:=HMIRecipe.DownloadBT);
CASE SaveStep OF
 0:
 IF rtRecipe1.Q AND HMIRecipe.IDChoose<>0 THEN
  HMIRecipe.LoadDone:=FALSE;
  SaveStep:=10;
 END_IF;
 10:
 HMIRecipe.CurrentPNName:=Zero;
 HMIRecipe.CurrentID:=HMIRecipe.IDChoose;
 IF HMIRecipe.CurrentPNName='                ' THEN
  SaveStep:=20;
 END_IF;
 20:
 HMIRecipe.CurrentPNName:=PNName[HMIRecipe.IDChoose];
 a:=1;
 FOR a:=1 TO 20 BY 1 DO
  MC_Data.AXIS1.Setting.rMovePosition[a]:=HMIRecipe.AxisData[HMIRecipe.IDChoose,1,a];
  MC_Data.AXIS2.Setting.rMovePosition[a]:=HMIRecipe.AxisData[HMIRecipe.IDChoose,2,a];
  MC_Data.AXIS3.Setting.rMovePosition[a]:=HMIRecipe.AxisData[HMIRecipe.IDChoose,3,a];
  MC_Data.AXIS4.Setting.rMovePosition[a]:=HMIRecipe.AxisData[HMIRecipe.IDChoose,4,a];
  MC_Data.AXIS5.Setting.rMovePosition[a]:=HMIRecipe.AxisData[HMIRecipe.IDChoose,5,a];
  MC_Data.AXIS6.Setting.rMovePosition[a]:=HMIRecipe.AxisData[HMIRecipe.IDChoose,6,a];
  MC_Data.AXIS7.Setting.rMovePosition[a]:=HMIRecipe.AxisData[HMIRecipe.IDChoose,7,a];
  MC_Data.AXIS8.Setting.rMovePosition[a]:=HMIRecipe.AxisData[HMIRecipe.IDChoose,8,a];
  MC_Data.AXIS9.Setting.rMovePosition[a]:=HMIRecipe.AxisData[HMIRecipe.IDChoose,9,a];
  MC_Data.AXIS10.Setting.rMovePosition[a]:=HMIRecipe.AxisData[HMIRecipe.IDChoose,10,a];
  MC_Data.AXIS11.Setting.rMovePosition[a]:=HMIRecipe.AxisData[HMIRecipe.IDChoose,11,a];
 END_FOR;
 SaveStep:=30;
 30:
 HMIRecipe.LoadDone:=TRUE;
 SaveStep:=0;
END_CASE;

////配方参数————>界面(保存)
rtRecipe2(Clk:=HMIRecipe.SaveBT);
IF rtRecipe2.Q AND HMIRecipe.IDChoose<>0 THEN
 PNName[HMIRecipe.IDChoose]:=HMIRecipe.ChoosePNName;
 b:=1;
 FOR b:=1 TO 20 BY 1 DO
  HMIRecipe.AxisData[HMIRecipe.IDChoose,1,b]:=MC_Data.AXIS1.Setting.rMovePosition[b];
  HMIRecipe.AxisData[HMIRecipe.IDChoose,2,b]:=MC_Data.AXIS2.Setting.rMovePosition[b];
  HMIRecipe.AxisData[HMIRecipe.IDChoose,3,b]:=MC_Data.AXIS3.Setting.rMovePosition[b];
  HMIRecipe.AxisData[HMIRecipe.IDChoose,4,b]:=MC_Data.AXIS4.Setting.rMovePosition[b];
  HMIRecipe.AxisData[HMIRecipe.IDChoose,5,b]:=MC_Data.AXIS5.Setting.rMovePosition[b];
  HMIRecipe.AxisData[HMIRecipe.IDChoose,6,b]:=MC_Data.AXIS6.Setting.rMovePosition[b];
  HMIRecipe.AxisData[HMIRecipe.IDChoose,7,b]:=MC_Data.AXIS7.Setting.rMovePosition[b];
  HMIRecipe.AxisData[HMIRecipe.IDChoose,8,b]:=MC_Data.AXIS8.Setting.rMovePosition[b];
  HMIRecipe.AxisData[HMIRecipe.IDChoose,9,b]:=MC_Data.AXIS9.Setting.rMovePosition[b];
  HMIRecipe.AxisData[HMIRecipe.IDChoose,10,b]:=MC_Data.AXIS10.Setting.rMovePosition[b];
  HMIRecipe.AxisData[HMIRecipe.IDChoose,11,b]:=MC_Data.AXIS11.Setting.rMovePosition[b];
 END_FOR;
 HMIRecipe.CurrentPNName:=Zero;
 HMIRecipe.SaveDone:=TRUE;
END_IF;

//选择名称切换时切换
ChooseDelay(In:=HMIRecipe.ChooseIDChanged, PT:=T#500ms);
ChooseDelay1(In:=HMIRecipe.ChooseIDChanged, PT:=T#1000ms);
ChooseDelay2(Clk:=ChooseDelay1.Q);
ChooseDelay3(Clk:=ChooseDelay.Q);
IF ChooseDelay3.Q THEN
 HMIRecipe.ChoosePNName:=Zero;
END_IF;
IF ChooseDelay2.Q THEN
 HMIRecipe.ChoosePNName:=PNName[HMIRecipe.IDChoose];
 HMIRecipe.ChooseIDChanged:=FALSE;
END_IF;