// ==================================================
// Cylinder_Action - 公司模板生成版
// 由 PLC数字工程师 根据公司模板自动生成
// ==================================================

//CY1_拨料上下气缸
CY1(CylinderData:=Cylinder_Data.CY1, Machine:=Machine_Data,
        bHP_Sensor:=I1_0 AND I1_3, bWP_Sensor:=I1_1 AND I1_4,
        bHP_Valve=>Q1_7, bWP_Valve=>Q1_6);
Cylinder_Data.CY1.Input.bOnILC:=TRUE;
Cylinder_Data.CY1.Input.bOffILC:=TRUE;

//CY2_NG剔除气缸
CY2(CylinderData:=Cylinder_Data.CY2, Machine:=Machine_Data,
        bHP_Sensor:=I2_0, bWP_Sensor:=I2_1,
        bHP_Valve=>Q2_0, bWP_Valve=>Q2_1);
Cylinder_Data.CY2.Input.bOnILC:=TRUE;
Cylinder_Data.CY2.Input.bOffILC:=TRUE;
