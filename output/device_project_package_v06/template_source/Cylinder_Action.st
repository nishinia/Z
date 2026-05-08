//CY1_拨料上下气缸
                    CY1(CylinderData:=Cylinder_Data.CY1, Machine:=Machine_Data, 
                              bHP_Sensor:=I1_0 AND I1_3, bWP_Sensor:=I1_1 AND I1_4, 
                              bHP_Valve=>Q1_7 , bWP_Valve=>Q1_6);
                            Cylinder_Data.CY1.Input.bOnILC:=TRUE;;
                    Cylinder_Data.CY1.Input.bOffILC:=TRUE;
     
     
(*// CY2_焊接定位气缸
          CY2(CylinderData:=Cylinder_Data.CY2, Machine:=Machine_Data, 
                              bHP_Sensor:=I1_6, bWP_Sensor:=I1_7, 
                              bHP_Valve=>Empty[1] , bWP_Valve=>Q1_7);
                    Cylinder_Data.CY2.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY2.Input.bOffILC:=TRUE;
//CY3SBX200组装上顶气缸
     CY3(CylinderData:=Cylinder_Data.CY3, Machine:=Machine_Data, 
                              bHP_Sensor:=I3_0, bWP_Sensor:=I3_1, 
                              bHP_Valve=>Empty[2] , bWP_Valve=>Q6_2);
                    Cylinder_Data.CY3.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY3.Input.bOffILC:=TRUE;
// CY4SBX100组装定位气缸
     CY4(CylinderData:=Cylinder_Data.CY4, Machine:=Machine_Data, 
                              bHP_Sensor:=I3_4, bWP_Sensor:=I3_5, 
                              bHP_Valve=>Empty[3] , bWP_Valve=>Q6_3);
                    Cylinder_Data.CY4.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY4.Input.bOffILC:=TRUE;
// CY5SBX100组装上顶气缸
     CY5(CylinderData:=Cylinder_Data.CY5, Machine:=Machine_Data, 
                              bHP_Sensor:=I3_6, bWP_Sensor:=I3_7, 
                              bHP_Valve=>Empty[4] , bWP_Valve=>Q6_4);
                    Cylinder_Data.CY5.Input.bOnILC:=TRUE;;
                    Cylinder_Data.CY5.Input.bOffILC:=TRUE;
// CY6SBX100检测气缸
     CY6(CylinderData:=Cylinder_Data.CY6, Machine:=Machine_Data, 
                              bHP_Sensor:=I4_0, bWP_Sensor:=I4_1, 
                              bHP_Valve=>Empty[5] , bWP_Valve=>Q6_5);
                    Cylinder_Data.CY6.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY6.Input.bOffILC:=TRUE;
//  CY7焊接定位气缸
     CY7(CylinderData:=Cylinder_Data.CY7, Machine:=Machine_Data, 
                              bHP_Sensor:=I5_4, bWP_Sensor:=I5_5, 
                              bHP_Valve=>Empty[6] , bWP_Valve=>Q6_6);
                    Cylinder_Data.CY7.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY7.Input.bOffILC:=TRUE;
//  CY8焊接上顶气缸
     CY8(CylinderData:=Cylinder_Data.CY8, Machine:=Machine_Data, 
                              bHP_Sensor:=I5_6, bWP_Sensor:=I5_7, 
                              bHP_Valve=>Empty[7] , bWP_Valve=>Q6_7);
                    Cylinder_Data.CY8.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY8.Input.bOffILC:=TRUE;
 // CY9成品料检测上下气缸
     CY9(CylinderData:=Cylinder_Data.CY9, Machine:=Machine_Data, 
                              bHP_Sensor:=I6_0, bWP_Sensor:=I6_1, 
                              bHP_Valve=>Empty[8] , bWP_Valve=>Q7_0);
                    Cylinder_Data.CY9.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY9.Input.bOffILC:=TRUE;
 //  CY10出料Wafer压料上下气缸
     CY10(CylinderData:=Cylinder_Data.CY10, Machine:=Machine_Data, 
                              bHP_Sensor:=I6_2, bWP_Sensor:=I6_3, 
                              bHP_Valve=>Empty[9] , bWP_Valve=>Q7_1);
                    Cylinder_Data.CY10.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY10.Input.bOffILC:=TRUE;
 // CY111#拨料定位气缸
     CY11(CylinderData:=Cylinder_Data.CY11, Machine:=Machine_Data, 
                              bHP_Sensor:=I4_2 AND I4_4 AND I4_6, bWP_Sensor:=I4_3 AND I4_5 AND I4_7, 
                              bHP_Valve=>Empty[10] , bWP_Valve=>Q7_2);
                    Cylinder_Data.CY11.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY11.Input.bOffILC:=TRUE;
 // CY122#拨料定位气缸
(*     CY12(CylinderData:=Cylinder_Data.CY12, Machine:=Machine_Data, 
                              bHP_Sensor:=TRUE, bWP_Sensor:=TRUE,
                              bHP_Valve=>Empty[11], bWP_Valve=>Q7_3);
                    Cylinder_Data.CY12.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY12.Input.bOffILC:=TRUE;*)
 //  CY133#拨料定位气缸
(*     CY13(CylinderData:=Cylinder_Data.CY13, Machine:=Machine_Data, 
                              bHP_Sensor:=TRUE, bWP_Sensor:=TRUE, 
                              bHP_Valve=>Empty[16] , bWP_Valve=>Q7_4);
                    Cylinder_Data.CY13.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY13.Input.bOffILC:=TRUE;*)
(* //  CY14SBX200压料上下气缸
     CY14(CylinderData:=Cylinder_Data.CY14, Machine:=Machine_Data, 
                              bHP_Sensor:=I7_2, bWP_Sensor:=I7_3, 
                              bHP_Valve=>Empty[15] , bWP_Valve=>Q7_5);
                    Cylinder_Data.CY14.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY14.Input.bOffILC:=TRUE;
 //CY15SBX200定位上下气缸
     CY15(CylinderData:=Cylinder_Data.CY15, Machine:=Machine_Data, 
                              bHP_Sensor:=I7_4, bWP_Sensor:=not I7_4, 
                              bHP_Valve=>Empty[16] , bWP_Valve=>Q7_6);
                    Cylinder_Data.CY15.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY15.Input.bOffILC:=TRUE;
 //CY16SBX200取料真空吸
     CY16(CylinderData:=Cylinder_Data.CY16, Machine:=Machine_Data, 
                              bHP_Sensor:=I7_6 OR TRUE, bWP_Sensor:=TRUE, 
                              bHP_Valve=>Q8_5 , bWP_Valve=>Q8_4);
                    Cylinder_Data.CY16.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY16.Input.bOffILC:=TRUE;
 //CY17SBX100压料上下气缸
     CY17(CylinderData:=Cylinder_Data.CY17, Machine:=Machine_Data, 
                              bHP_Sensor:=I8_2, bWP_Sensor:=I8_3, 
                              bHP_Valve=>Empty[16] , bWP_Valve=>Q8_0);
                    Cylinder_Data.CY17.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY17.Input.bOffILC:=TRUE;
 //CY18SBX100定位上下气缸
     CY18(CylinderData:=Cylinder_Data.CY18, Machine:=Machine_Data, 
                              bHP_Sensor:=I8_4, bWP_Sensor:=not I8_4, 
                              bHP_Valve=>Empty[16] , bWP_Valve=>Q8_1);
                    Cylinder_Data.CY18.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY18.Input.bOffILC:=TRUE;
 //CY19SBX100取料真空吸
     CY19(CylinderData:=Cylinder_Data.CY19, Machine:=Machine_Data, 
                              bHP_Sensor:=I8_6 OR TRUE, bWP_Sensor:=TRUE, 
                              bHP_Valve=>Q8_7 , bWP_Valve=>Q8_6);
                    Cylinder_Data.CY19.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY19.Input.bOffILC:=TRUE;
 //CY20_SBX200裁切真空吸
     CY20(CylinderData:=Cylinder_Data.CY20, Machine:=Machine_Data, 
                              bHP_Sensor:=I7_7 OR TRUE, bWP_Sensor:=TRUE, 
                              bHP_Valve=>Q10_1 , bWP_Valve=>Q10_0);
                    Cylinder_Data.CY20.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY20.Input.bOffILC:=TRUE;
 //CY21_SBX100裁切真空吸
     CY21(CylinderData:=Cylinder_Data.CY21, Machine:=Machine_Data, 
                              bHP_Sensor:=I8_7 OR TRUE, bWP_Sensor:=TRUE, 
                              bHP_Valve=>Q10_3 , bWP_Valve=>Q10_2);
                    Cylinder_Data.CY21.Input.bOnILC:=TRUE;
                    Cylinder_Data.CY21.Input.bOffILC:=TRUE;
*)
(*Cylinder_Data.CY1.Input.tHP_Delay:=100;
Cylinder_Data.CY2.Input.tHP_Delay:=100;
Cylinder_Data.CY3.Input.tHP_Delay:=100;
Cylinder_Data.CY4.Input.tHP_Delay:=100;
Cylinder_Data.CY5.Input.tHP_Delay:=100;
Cylinder_Data.CY6.Input.tHP_Delay:=100;
Cylinder_Data.CY7.Input.tHP_Delay:=100;
Cylinder_Data.CY8.Input.tHP_Delay:=100;
Cylinder_Data.CY9.Input.tHP_Delay:=100;
Cylinder_Data.CY10.Input.tHP_Delay:=100;
Cylinder_Data.CY11.Input.tHP_Delay:=100;
Cylinder_Data.CY12.Input.tHP_Delay:=100;
Cylinder_Data.CY13.Input.tHP_Delay:=100;
Cylinder_Data.CY14.Input.tHP_Delay:=100;
Cylinder_Data.CY15.Input.tHP_Delay:=100;
Cylinder_Data.CY16.Input.tHP_Delay:=100;
Cylinder_Data.CY17.Input.tHP_Delay:=100;
Cylinder_Data.CY18.Input.tHP_Delay:=100;
Cylinder_Data.CY19.Input.tHP_Delay:=100;
Cylinder_Data.CY20.Input.tHP_Delay:=100;
Cylinder_Data.CY21.Input.tHP_Delay:=100;

Cylinder_Data.CY1.Input.tWP_Delay:=100;
Cylinder_Data.CY2.Input.tWP_Delay:=100;
Cylinder_Data.CY3.Input.tWP_Delay:=100;
Cylinder_Data.CY4.Input.tWP_Delay:=100;
Cylinder_Data.CY5.Input.tWP_Delay:=100;
Cylinder_Data.CY6.Input.tWP_Delay:=100;
Cylinder_Data.CY7.Input.tWP_Delay:=100;
Cylinder_Data.CY8.Input.tWP_Delay:=100;
Cylinder_Data.CY9.Input.tWP_Delay:=100;
Cylinder_Data.CY10.Input.tWP_Delay:=100;
Cylinder_Data.CY11.Input.tWP_Delay:=100;
Cylinder_Data.CY12.Input.tWP_Delay:=100;
Cylinder_Data.CY13.Input.tWP_Delay:=100;
Cylinder_Data.CY14.Input.tWP_Delay:=100;
Cylinder_Data.CY15.Input.tWP_Delay:=100;
Cylinder_Data.CY16.Input.tWP_Delay:=100;
Cylinder_Data.CY17.Input.tWP_Delay:=100;
Cylinder_Data.CY18.Input.tWP_Delay:=100;
Cylinder_Data.CY19.Input.tWP_Delay:=100;
Cylinder_Data.CY20.Input.tWP_Delay:=100;
Cylinder_Data.CY21.Input.tWP_Delay:=100;*)