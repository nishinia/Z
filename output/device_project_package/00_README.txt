PLC数字工程师 V0.4.2 工程包

项目名称：AI_Device_Project_V051
PLC：Omron NJ501
生成时间：2026-05-08 02:03:23
生成器：PLC数字工程师
模板版本：company_template_v0.1

项目说明：
项目说明

文件说明：
1. 00_README.txt
   - 工程包说明文件

2. validation_report.txt
   - 自动校验报告
   - 检查气缸配置、工站配置、报警配置、模板源文件、公司符号配置等

3. manifest.json
   - 工程包清单
   - 记录生成器版本、生成时间、文件列表、文件大小、SHA256校验值

4. 01_Cylinder_Action_Generated.st
   - 公司模板风格气缸动作调用程序
   - 由 configs/cylinder_config.json 渲染生成

5. 02_Station_Generated.st
   - 公司模板风格工站自动流程程序
   - 包含 Station[_StationNum].nAutoStep
   - 支持超时报警、安全停机、完成复位
   - 由 configs/station_config.json 渲染生成

6. configs/cylinder_config.json
   - 气缸配置

7. configs/station_config.json
   - 工站流程配置

8. configs/company_symbols.json
   - 公司命名配置
   - 修改这里可以适配不同项目字段名

9. template_source/
   - 从公司原始项目提取出的模板参考文件

注意：
- 本工程包为自动生成模板，不能直接下载到真实PLC。
- 必须经过工程师审核、Sysmac Studio 编译、仿真、空载验证、现场调试。
- 急停、安全门、光栅等安全功能必须走硬件安全回路。
- manifest.json 仅用于追踪生成信息，不代表程序已通过现场验证。
- validation_report.txt 仅为基础规则校验，不能替代工程师审核。