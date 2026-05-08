# 用户说明书 - PLC数字工程师 V0.7.0

## 一、启动软件

方法一：

cd /d D:\AI\plc_ai_system
streamlit run app_product.py

方法二：

双击：

start_plc_digital_engineer_v070.bat

## 二、操作流程

### 1. 输入整机中文需求

建议包含：

- 项目名称
- PLC 型号
- 气缸清单
- IO 点位
- 工站清单
- 每个工站流程
- 超时报警要求
- 复位要求
- 工站之间的顺序关系

### 2. 点击 AI 解析

点击页面中的：

🤖 第一步：AI解析整机需求

### 3. 人工确认

重点检查：

- 气缸数量是否正确
- 工站数量是否正确
- S1/S2/S3 顺序是否正确
- 每个工站步骤是否正确
- 报警和超时是否正确
- 复位要求是否被识别

### 4. 生成最终工程包

点击：

📦 第二步：生成 V0.7.0 最终工程包 ZIP

### 5. 下载 ZIP

点击：

⬇️ 下载 V0.7.0 最终工程包 ZIP

默认文件名：

AI_Device_Project_Package_V070_Final.zip

## 三、最终 ZIP 包内容

- 00_README.txt
- validation_report.txt
- manifest.json
- 00_DUT_Struct_Generated.st
- 00_Global_Variables_Generated.st
- 01_Cylinder_Action_Generated.st
- 02_Station_S1_Auto_Generated.st
- 03_Station_S2_Auto_Generated.st
- 04_Machine_Auto_Main_Generated.st
- HMI_Variable_List.csv
- IO_Mapping_List.csv
- IO_Mapping_Enhanced.csv
- Alarm_List.csv
- Step_List.csv
- Variable_CrossReference_Report.txt
- Final_Acceptance_Report.txt
- Sysmac_Import_Guide.txt
- ST_Quality_Report.txt
- configs/
- template_source/

## 四、注意事项

这个工具是工程辅助工具，不替代 PLC 工程师。

最终投产前必须完成 IO 地址复核、设备动作安全评审、单步调试、空跑验证、带料验证、急停和安全门测试。
