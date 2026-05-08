I0_0	BOOL	BuiltInIO://cpu/#0/Input_Bit_00	False	False	公开	启动按钮
I0_1	BOOL	BuiltInIO://cpu/#0/Input_Bit_01	False	False	公开	复位按钮
I0_2	BOOL	BuiltInIO://cpu/#0/Input_Bit_02	False	False	公开	停止按钮
I0_3	BOOL	BuiltInIO://cpu/#0/Input_Bit_03	False	False	公开	工安按钮
I0_4	BOOL	BuiltInIO://cpu/#0/Input_Bit_04	False	False	公开	手/自动
I0_5	BOOL	BuiltInIO://cpu/#0/Input_Bit_05	False	False	公开	前界面急停
I0_6	BOOL	BuiltInIO://cpu/#0/Input_Bit_06	False	False	公开	放料急停
I0_7	BOOL	BuiltInIO://cpu/#0/Input_Bit_07	False	False	公开	气压表
I0_8	BOOL	BuiltInIO://cpu/#0/Input_Bit_08	False	False	公开	安全门1
I0_9	BOOL	BuiltInIO://cpu/#0/Input_Bit_09	False	False	公开	安全门2
I0_10	BOOL	BuiltInIO://cpu/#0/Input_Bit_10	False	False	公开	安全门3
I0_11	BOOL	BuiltInIO://cpu/#0/Input_Bit_11	False	False	公开	安全门4
I0_12	BOOL	BuiltInIO://cpu/#0/Input_Bit_12	False	False	公开	裁切到位1
I0_13	BOOL	BuiltInIO://cpu/#0/Input_Bit_13	False	False	公开	裁切到位2
I0_14	BOOL	BuiltInIO://cpu/#0/Input_Bit_14	False	False	公开	裁切到位3
I0_15	BOOL	BuiltInIO://cpu/#0/Input_Bit_15	False	False	公开
I1_0	BOOL	BuiltInIO://cpu/#0/Input_Bit_16	False	False	公开	CY1_拨料1上下气缸原点
I1_1	BOOL	BuiltInIO://cpu/#0/Input_Bit_17	False	False	公开	CY1_拨料1上下气缸动点
I1_2	BOOL	BuiltInIO://cpu/#0/Input_Bit_18	False	False	公开	拨料1防呆感应（槽型光电）
I1_3	BOOL	BuiltInIO://cpu/#0/Input_Bit_19	False	False	公开	CY1_拨料2上下气缸原点
I1_4	BOOL	BuiltInIO://cpu/#0/Input_Bit_20	False	False	公开	CY1_拨料2上下气缸动点
I1_5	BOOL	BuiltInIO://cpu/#0/Input_Bit_21	False	False	公开	拨料2防呆感应（槽型光电）
I1_6	BOOL	BuiltInIO://cpu/#0/Input_Bit_22	False	False	公开	拨料到位信号
I1_7	BOOL	BuiltInIO://cpu/#0/Input_Bit_23	False	False	公开
Q0_0	BOOL	BuiltInIO://cpu/#0/Output_Bit_00	False	False	公开	启动按钮灯
Q0_1	BOOL	BuiltInIO://cpu/#0/Output_Bit_01	False	False	公开	复位按钮灯
Q0_2	BOOL	BuiltInIO://cpu/#0/Output_Bit_02	False	False	公开	停止按钮灯
Q0_3	BOOL	BuiltInIO://cpu/#0/Output_Bit_03	False	False	公开	工安按钮灯
Q0_4	BOOL	BuiltInIO://cpu/#0/Output_Bit_04	False	False	公开	三色灯 红
Q0_5	BOOL	BuiltInIO://cpu/#0/Output_Bit_05	False	False	公开	三色灯 黄
Q0_6	BOOL	BuiltInIO://cpu/#0/Output_Bit_06	False	False	公开	三色灯 绿
Q0_7	BOOL	BuiltInIO://cpu/#0/Output_Bit_07	False	False	公开	三色灯 蜂鸣器
Q1_0	BOOL	BuiltInIO://cpu/#0/Output_Bit_08	False	False	公开	缓慢上气阀
Q1_1	BOOL	BuiltInIO://cpu/#0/Output_Bit_09	False	False	公开	日光灯_KA1
Q1_2	BOOL	BuiltInIO://cpu/#0/Output_Bit_10	False	False	公开	安全门1锁
Q1_3	BOOL	BuiltInIO://cpu/#0/Output_Bit_11	False	False	公开	安全门2锁
Q1_4	BOOL	BuiltInIO://cpu/#0/Output_Bit_12	False	False	公开	安全门3锁
Q1_5	BOOL	BuiltInIO://cpu/#0/Output_Bit_13	False	False	公开	安全门4锁
Q1_6	BOOL	BuiltInIO://cpu/#0/Output_Bit_14	False	False	公开	CY1_Water拨料上下气缸电磁阀出
Q1_7	BOOL	BuiltInIO://cpu/#0/Output_Bit_15	False	False	公开	CY1_Water拨料上下气缸电磁阀回
Cylinder_Data	CylinderName	True	False	公开
MC_Data	ServoName	True	False	公开
Machine_Data	ST_Machine	False	False	公开
Machine_Alarm	ST_Alarm	False	False	公开
nInitStep	UINT	False	False	不公开
Station	ARRAY[1..20] OF ST_Station	False	False	公开
Hmi	ST_HMI	False	False	公开
KeepBool	ST_KeepBool	True	False	公开
互锁	工位交互信号	False	False	不公开
Sensor_Data	SesorName	False	False	不公开
Motor1Control	ST_Motor	False	False	公开
Motor1Setting	ST_MotorSetting	True	False	公开
Motor2Control	ST_Motor	False	False	公开
Motor2Setting	ST_MotorSetting	True	False	公开
屏蔽片尾料模式	BOOL	False	False	公开
Motor3Control	ST_Motor	False	False	公开
Motor3Setting	ST_MotorSetting	True	False	公开
Motor4Control	ST_Motor	False	False	公开
Motor4Setting	ST_MotorSetting	True	False	公开
Motor5Control	ST_Motor	False	False	公开
Motor5Setting	ST_MotorSetting	True	False	公开
加固片尾料模式	BOOL	False	False	公开
焊接后端尾料模式	BOOL	False	False	公开
CCD触发	BOOL	False	False	公开
CCD连续不良数设置	UINT	True	False	公开
预计产能	REAL	True	False	公开
实际产能	REAL	True	False	公开
易损件报警	BOOL	False	False	公开
总计数	BOOL	False	False	公开
I2_0	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit0_6000_01	False	False	公开	放料启动按钮
I2_1	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit1_6000_02	False	False	公开	放料感应
I2_2	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit2_6000_03	False	False	公开	收料料启动按钮
I2_3	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit3_6000_04	False	False	公开	收料感应
I2_4	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit4_6000_05	False	False	公开	安全门5
I2_5	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit5_6000_06	False	False	公开	安全门6
I2_6	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit6_6000_07	False	False	公开	安全光栅1
I2_7	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit7_6000_08	False	False	公开	安全光栅2
I3_0	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit8_6000_09	False	False	公开	涂油完成信号
I3_1	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit9_6000_0A	False	False	公开	涂油报警信号
I3_2	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit10_6000_0B	False	False	公开	油桶缺油信号
I3_3	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit11_6000_0C	False	False	公开	涂油有料感应
I3_4	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit12_6000_0D	False	False	公开	烤箱温度正常
I3_5	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit13_6000_0E	False	False	公开	裁切后除静电放电信号
I3_6	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit14_6000_0F	False	False	公开	裁切后除静电异常信号
I3_7	BOOL	ECAT://node#[1,0]/1600END input-bit maping_Digital input bit15_6000_10	False	False	公开	裁切后除静电维护信号
I4_0	BOOL	ECAT://node#[1,2]/0808ETN input-bit maping_Digital input bit0_6000_01	False	False	公开
I4_1	BOOL	ECAT://node#[1,2]/0808ETN input-bit maping_Digital input bit1_6000_02	False	False	公开
I4_2	BOOL	ECAT://node#[1,2]/0808ETN input-bit maping_Digital input bit2_6000_03	False	False	公开
I4_3	BOOL	ECAT://node#[1,2]/0808ETN input-bit maping_Digital input bit3_6000_04	False	False	公开
I4_4	BOOL	ECAT://node#[1,2]/0808ETN input-bit maping_Digital input bit4_6000_05	False	False	公开
I4_5	BOOL	ECAT://node#[1,2]/0808ETN input-bit maping_Digital input bit5_6000_06	False	False	公开
I4_6	BOOL	ECAT://node#[1,2]/0808ETN input-bit maping_Digital input bit6_6000_07	False	False	公开
I4_7	BOOL	ECAT://node#[1,2]/0808ETN input-bit maping_Digital input bit7_6000_08	False	False	公开
I5_0	BOOL	False	False	公开
I5_1	BOOL	False	False	公开
I5_2	BOOL	False	False	公开
I5_3	BOOL	False	False	公开
I5_4	BOOL	False	False	公开
I5_5	BOOL	False	False	公开
I5_6	BOOL	False	False	公开
I5_7	BOOL	False	False	公开
I6_0	BOOL	False	False	公开
I6_1	BOOL	False	False	公开
I6_2	BOOL	False	False	公开
I6_3	BOOL	False	False	公开
I6_4	BOOL	False	False	公开
I6_5	BOOL	False	False	公开
I6_6	BOOL	False	False	公开
I6_7	BOOL	False	False	公开
I7_0	BOOL	False	False	公开
I7_1	BOOL	False	False	公开
I7_2	BOOL	False	False	公开
I7_3	BOOL	False	False	公开
I7_4	BOOL	False	False	公开
I7_5	BOOL	False	False	公开
I7_6	BOOL	False	False	公开
I7_7	BOOL	False	False	公开
I8_0	BOOL	False	False	公开
I8_1	BOOL	False	False	公开
I8_2	BOOL	False	False	公开
I8_3	BOOL	False	False	公开
I8_4	BOOL	False	False	公开
I8_5	BOOL	False	False	公开
I8_6	BOOL	False	False	公开
I8_7	BOOL	False	False	公开
I9_0	BOOL	False	False	公开
I9_1	BOOL	False	False	公开
I9_2	BOOL	False	False	公开
I9_3	BOOL	False	False	公开
I9_4	BOOL	False	False	公开
I9_5	BOOL	False	False	公开
I9_6	BOOL	False	False	公开
I9_7	BOOL	False	False	公开
I10_0	BOOL	False	False	公开
I10_1	BOOL	False	False	公开
I10_2	BOOL	False	False	公开
I10_3	BOOL	False	False	公开
I10_4	BOOL	False	False	公开
I10_5	BOOL	False	False	公开
I10_6	BOOL	False	False	公开
I10_7	BOOL	False	False	公开
I11_0	BOOL	False	False	公开
I11_1	BOOL	False	False	公开
I11_2	BOOL	False	False	公开
I11_3	BOOL	False	False	公开
I11_4	BOOL	False	False	公开
I11_5	BOOL	False	False	公开
I11_6	BOOL	False	False	公开
I11_7	BOOL	False	False	公开
I12_0	BOOL	False	False	公开
I12_1	BOOL	False	False	公开
I12_2	BOOL	False	False	公开
I12_3	BOOL	False	False	公开
I12_4	BOOL	False	False	公开
I12_5	BOOL	False	False	公开
I12_6	BOOL	False	False	公开
I12_7	BOOL	False	False	公开
I13_0	BOOL	False	False	公开
I13_1	BOOL	False	False	公开
I13_2	BOOL	False	False	公开
I13_3	BOOL	False	False	公开
I13_4	BOOL	False	False	公开
I13_5	BOOL	False	False	公开
I13_6	BOOL	False	False	公开
I13_7	BOOL	False	False	公开
I14_0	BOOL	False	False	公开
I14_1	BOOL	False	False	公开
I14_2	BOOL	False	False	公开
I14_3	BOOL	False	False	公开
I14_4	BOOL	False	False	公开
I14_5	BOOL	False	False	公开
I14_6	BOOL	False	False	公开
I14_7	BOOL	False	False	公开
Q2_0	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit0_7000_01	False	False	公开	放料马达
Q2_1	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit1_7000_02	False	False	公开	放料收纸马达
Q2_2	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit2_7000_03	False	False	公开	收料马达
Q2_3	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit3_7000_04	False	False	公开	收料收纸马达
Q2_4	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit4_7000_05	False	False	公开	放料马达按钮灯
Q2_5	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit5_7000_06	False	False	公开	收料马达按钮灯
Q2_6	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit6_7000_07	False	False	公开	裁切吸料控制
Q2_7	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit7_7000_08	False	False	公开
Q3_0	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit8_7000_09	False	False	公开	涂油启动控制
Q3_1	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit9_7000_0A	False	False	公开	裁切后吸尘控制
Q3_2	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit10_7000_0B	False	False	公开	裁切后除静电放电控制
Q3_3	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit11_7000_0C	False	False	公开	安全门5锁
Q3_4	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit12_7000_0D	False	False	公开	安全门6锁
Q3_5	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit13_7000_0E	False	False	公开
Q3_6	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit14_7000_0F	False	False	公开
Q3_7	BOOL	ECAT://node#[1,1]/0016ETN Output-bit maping_Digital output bit15_7000_10	False	False	公开
Q4_0	BOOL	ECAT://node#[1,2]/0808ETN Output-bit maping_Digital output bit0_7000_01	False	False	公开
Q4_1	BOOL	ECAT://node#[1,2]/0808ETN Output-bit maping_Digital output bit1_7000_02	False	False	公开
Q4_2	BOOL	ECAT://node#[1,2]/0808ETN Output-bit maping_Digital output bit2_7000_03	False	False	公开
Q4_3	BOOL	ECAT://node#[1,2]/0808ETN Output-bit maping_Digital output bit3_7000_04	False	False	公开
Q4_4	BOOL	ECAT://node#[1,2]/0808ETN Output-bit maping_Digital output bit4_7000_05	False	False	公开
Q4_5	BOOL	ECAT://node#[1,2]/0808ETN Output-bit maping_Digital output bit5_7000_06	False	False	公开
Q4_6	BOOL	ECAT://node#[1,2]/0808ETN Output-bit maping_Digital output bit6_7000_07	False	False	公开
Q4_7	BOOL	ECAT://node#[1,2]/0808ETN Output-bit maping_Digital output bit7_7000_08	False	False	公开
Q5_0	BOOL	False	False	公开
Q5_1	BOOL	False	False	公开
Q5_2	BOOL	False	False	公开
Q5_3	BOOL	False	False	公开
Q5_4	BOOL	False	False	公开
Q5_5	BOOL	False	False	公开
Q5_6	BOOL	False	False	公开
Q5_7	BOOL	False	False	公开
Q6_0	BOOL	False	False	公开
Q6_1	BOOL	False	False	公开
Q6_2	BOOL	False	False	公开
Q6_3	BOOL	False	False	公开
Q6_4	BOOL	False	False	公开
Q6_5	BOOL	False	False	公开
Q6_6	BOOL	False	False	公开
Q6_7	BOOL	False	False	公开
Q7_0	BOOL	False	False	公开
Q7_1	BOOL	False	False	公开
Q7_2	BOOL	False	False	公开
Q7_3	BOOL	False	False	公开
Q7_4	BOOL	False	False	公开
Q7_5	BOOL	False	False	公开
Q7_6	BOOL	False	False	公开
Q7_7	BOOL	False	False	公开
Q8_0	BOOL	False	False	公开
Q8_1	BOOL	False	False	公开
Q8_2	BOOL	False	False	公开
Q8_3	BOOL	False	False	公开
Q8_4	BOOL	False	False	公开
Q8_5	BOOL	False	False	公开
Q8_6	BOOL	False	False	公开
Q8_7	BOOL	False	False	公开
Q9_0	BOOL	False	False	公开
Q9_1	BOOL	False	False	公开
Q9_2	BOOL	False	False	公开
Q9_3	BOOL	False	False	公开
Q9_4	BOOL	False	False	公开
Q9_5	BOOL	False	False	公开
Q9_6	BOOL	False	False	公开
Q9_7	BOOL	False	False	公开
Q10_0	BOOL	False	False	公开
Q10_1	BOOL	False	False	公开
Q10_2	BOOL	False	False	公开
Q10_3	BOOL	False	False	公开
Q10_4	BOOL	False	False	公开
Q10_5	BOOL	False	False	公开
Q10_6	BOOL	False	False	公开
Q10_7	BOOL	False	False	公开
Q11_0	BOOL	False	False	公开
Q11_1	BOOL	False	False	公开
Q11_2	BOOL	False	False	公开
Q11_3	BOOL	False	False	公开
Q11_4	BOOL	False	False	公开
Q11_5	BOOL	False	False	公开
Q11_6	BOOL	False	False	公开
Q11_7	BOOL	False	False	公开
良品计数	BOOL	False	False	公开
不良计数	BOOL	False	False	公开
自由计数	ARRAY[1..20] OF BOOL	False	False	公开
停机触发	BOOL	False	False	公开
SBX200易损件计数	BOOL	False	False	公开
SBX100易损件计数	BOOL	False	False	公开
拨料易损件计数	BOOL	False	False	公开
To_Machine1	ARRAY[1..5] OF BOOL	False	False	输出
From_Machine1	ARRAY[1..5] OF BOOL	False	False	输入
To_Machine2	ARRAY[1..5] OF BOOL	False	False	输出
From_Machine2	ARRAY[1..5] OF BOOL	False	False	输入
To_Machine3	ARRAY[1..5] OF BOOL	False	False	输出
From_Machine3	ARRAY[1..5] OF BOOL	False	False	输入
To_Machine4	ARRAY[1..5] OF BOOL	False	False	输出
From_Machine4	ARRAY[1..5] OF BOOL	False	False	输入
To_Machine5	ARRAY[1..5] OF BOOL	False	False	输出
From_Machine5	ARRAY[1..5] OF BOOL	False	False	输入
To_Machine6	ARRAY[1..5] OF BOOL	False	False	输出
From_Machine6	ARRAY[1..5] OF BOOL	False	False	输入
To_Machine7	ARRAY[1..5] OF BOOL	False	False	输出
From_Machine7	ARRAY[1..5] OF BOOL	False	False	输入
To_Machine8	ARRAY[1..5] OF BOOL	False	False	输出
From_Machine8	ARRAY[1..5] OF BOOL	False	False	输入
weixiu_mode	BOOL	False	False	公开
All_weixiu_mode	BOOL	False	False	公开
I2	USINT	False	False	公开
I0	USINT	False	False	公开
I00	USINT	False	False	公开
I1	USINT	False	False	公开
I3	USINT	False	False	公开
I4	USINT	False	False	公开
I5	USINT	False	False	公开
I6	USINT	False	False	输入
I7	USINT	False	False	输入
I8	USINT	False	False	输入
I9	USINT	False	False	输入
I10	USINT	False	False	输入
I11	USINT	False	False	输入
I12	USINT	False	False	输入
I13	USINT	False	False	输入
I14	USINT	False	False	输入
Q0	USINT	False	False	输出
Q1	USINT	False	False	输出
Q2	USINT	False	False	输出
Q3	USINT	False	False	输出
Q4	USINT	False	False	输出
Q5	USINT	False	False	输出
Q6	USINT	False	False	输出
Q7	USINT	False	False	输出
Q8	USINT	False	False	输出
Q9	USINT	False	False	输出
Q10	USINT	False	False	输出
Q11	USINT	False	False	输出
PackageCountX	INT	False	False	不公开
PackageCountY	INT	False	False	不公开
PackageSettingX	INT	True	False	公开
PackageSettingY	INT	True	False	公开
LasereEnavailable	BOOL	True	False	公开	设置不适用激光焊接工位
HMIRecipe	RecipeData	True	False	公开
PNName	ARRAY[1..10] OF STRING[30]	True	False	不公开
HMILaserTrigBT	BOOL	False	False	公开
HMINoPackage	BOOL	True	False	公开
Wafer尾料BT	BOOL	False	False	公开
SBX200尾料BT	BOOL	False	False	公开
SBX100尾料BT	BOOL	False	False	公开
收料尾料BT	BOOL	False	False	公开
安全门屏蔽BT	BOOL	True	False	公开
消音器BT	BOOL	False	False	公开
吸尘器BT	BOOL	False	False	公开
Wafer进料吹气BT	BOOL	False	False	公开
Wafer出料吹气BT	BOOL	False	False	公开
bStep_Wafer	ARRAY[0..50] OF BOOL	False	False	公开
bStep_X200	ARRAY[0..50] OF BOOL	False	False	公开
bStep_X100	ARRAY[0..50] OF BOOL	False	False	公开
X200真空吸缺料补料按钮	BOOL	False	False	公开
X100真空吸缺料补料按钮	BOOL	False	False	公开
Axis1拨料伺服	_sAXIS_REF	MC://_MC_AX[0]	False	True	不公开
Axis2裁切伺服	_sAXIS_REF	MC://_MC_AX[1]	False	True	不公开
Axis3涂油伺服	_sAXIS_REF	MC://_MC_AX[2]	False	True	不公开
S1拨料完成	BOOL	False	False	不公开
S6裁切完成	BOOL	False	False	不公开
Axis3MovTigger	BOOL	False	False	公开
OilAuto	BOOL	False	False	公开
OilManual	BOOL	False	False	公开