PLC数字工程师 V0.7.1 多工站工程包

项目名称：AI_Device_Project_V071_Servo
PLC：Omron NJ501
生成时间：2026-05-08 06:49:17
生成器：PLC数字工程师
模板版本：company_template_v0.1

项目说明：
项目说明

工站列表：
- S1_Auto_Generated：S1_上料工站，工站号 1
- S2_Auto_Generated：S2_搬运工站，工站号 2

文件说明：
1. 00_README.txt
   - 工程包说明

2. validation_report.txt
   - 多工站自动校验报告

3. manifest.json
   - 工程包清单和文件 SHA256 追踪

4. 01_Cylinder_Action_Generated.st
   - 气缸动作统一调用程序

5. 02_Station_xxx.st / 03_Station_xxx.st
   - 多个工站自动流程程序

6. configs/
   - cylinder_config.json
   - station_configs.json
   - company_symbols.json

7. template_source/
   - 公司模板参考源码

注意：
- 本工程包不能直接下载到真实 PLC。
- 必须经工程师审核、Sysmac Studio 编译、仿真、空载测试、现场调试。
- 多工站之间的互锁、交互信号，需要工程师根据实际节拍补充。