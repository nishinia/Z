\# PLC数字工程师项目版本记录



\## V0.6.1 - 已封版



封版时间：2026-05-08



\### 核心能力



\- 整机中文需求解析为多工站 station\_configs

\- 支持 S1 / S2 多工站识别

\- 支持多工站 ZIP 工程包生成

\- 支持 manifest.json 追踪清单

\- 支持 validation\_report.txt 自动校验报告

\- 支持 configs 目录输出

\- 支持 template\_source 模板追踪

\- 支持 S1 / S2 工站 ST 文件生成

\- 支持报警 / 超时 / 复位基础逻辑



\### 验收结果



\- ZIP 基础结构检查通过

\- V0.6.1 逻辑检查通过

\- V0.6.1 最终验收通过

\- 已生成源码备份：V0.6.1\_source\_backup.zip



\### 下一版本



V0.6.2：整机主流程 + 多工站互锁增强

\## V0.6.2 - 已封版



封版时间：2026-05-08



\### 核心能力



\- 基于 V0.6.1 多工站工程包自动升级为 V0.6.2 工程包

\- 新增整机主流程 ST：04\_Machine\_Auto\_Main\_Generated.st

\- 新增 HMI 变量清单：HMI\_Variable\_List.csv

\- 新增多工站顺序互锁

\- 支持 S1 完成后允许 S2 执行

\- 支持最后工站完成后整机完成

\- 支持任意工站报警汇总到整机报警

\- 支持 Reset 统一复位所有工站

\- 新增 configs/v062\_station\_chain.json

\- 自动更新 manifest.json

\- 自动更新 validation\_report.txt



\### 验收结果



\- V0.6.2 ZIP 文件结构检查通过

\- 整机主流程 ST 检查通过

\- HMI 变量清单检查通过

\- validation\_report V0.6.2 信息检查通过



\### 当前生成结果



\- AI\_Device\_Project\_Package\_V06\_V0.6.2.zip



\### 下一版本



V0.6.2.1：把 V0.6.2 外挂升级逻辑正式合并进主工程生成器

\## V0.6.2.1 - 已封版



封版时间：2026-05-08



\### 核心能力



\- 将 V0.6.2 外挂升级能力正式合并进主工程生成器

\- 新增 machine\_main\_generator.py

\- 新增 hmi\_variable\_generator.py

\- multi\_station\_project\_generator.py 直接生成整机主流程 ST

\- multi\_station\_project\_generator.py 直接生成 HMI 变量清单

\- 自动生成 04\_Machine\_Auto\_Main\_Generated.st

\- 自动生成 HMI\_Variable\_List.csv

\- 自动生成 configs/v062\_station\_chain.json

\- manifest.json 写入 V0.6.2.1 版本信息

\- validation\_report.txt 写入 V0.6.2.1 验收信息



\### 验收结果



\- Python 编译检查通过

\- 主生成器直接生成 ZIP 通过

\- V0.6.2.1 集成验收通过



\### 当前稳定输出



\- output/AI\_Device\_Project\_Package\_V06.zip



\### 下一版本



V0.6.2.2：Streamlit 界面端验收与版本显示同步





\## V0.6.2.2 - 已封版



封版时间：2026-05-08



\### 核心能力



\- Streamlit 网页端已接入 V0.6.2.1 主生成器

\- 网页端可直接通过整机中文需求生成多工站工程包

\- 网页端生成 ZIP 已包含整机主流程 ST

\- 网页端生成 ZIP 已包含 HMI 变量清单

\- 网页端生成 ZIP 已包含工站链路配置

\- 下载包包含 04\_Machine\_Auto\_Main\_Generated.st

\- 下载包包含 HMI\_Variable\_List.csv

\- 下载包包含 configs/v062\_station\_chain.json



\### 验收结果



\- 网页端生成 ZIP 通过

\- 整机主流程 ST 检查通过

\- HMI 变量清单检查通过

\- manifest 检查通过

\- validation\_report 检查通过



\### 当前稳定输出



\- output/AI\_Device\_Project\_Package\_V06.zip



\### 下一版本



V0.6.3：Sysmac Studio 导入前工程规范增强

\## V0.6.3 - 已封版



封版时间：2026-05-08



\### 核心能力



\- 新增 Sysmac Studio 导入前工程规范增强

\- 新增 00\_DUT\_Struct\_Generated.st

\- 新增 00\_Global\_Variables\_Generated.st

\- 新增 IO\_Mapping\_List.csv

\- 新增 Sysmac\_Import\_Guide.txt

\- 新增 ST\_Quality\_Report.txt

\- 生成 DUT / STRUCT 类型声明

\- 生成全局变量声明建议

\- 生成 IO 映射清单

\- 生成 Sysmac Studio 导入说明

\- 生成 ST 静态质量检查报告

\- manifest.json 写入 V0.6.3 信息

\- validation\_report.txt 写入 V0.6.3 验收信息



\### 验收结果



\- V0.6.3 自动生成工程包通过

\- ZIP 必要文件检查通过

\- DUT 结构检查通过

\- 全局变量检查通过

\- IO 映射 CSV 检查通过

\- Sysmac 导入说明检查通过

\- ST 质量报告检查通过

\- manifest / validation 检查通过



\### 当前稳定输出



\- output/AI\_Device\_Project\_Package\_V06.zip



\### 下一版本



V0.6.4：ST变量引用一致性检查 + IO地址解析增强 + 报警清单生成

\## V0.6.4 - 已封版



封版时间：2026-05-08



\### 核心能力



\- 新增 Alarm\_List.csv 报警清单

\- 新增 Step\_List.csv 工站步骤清单

\- 新增 IO\_Mapping\_Enhanced.csv 增强 IO 映射

\- 新增 Variable\_CrossReference\_Report.txt 变量交叉引用报告

\- 新增 Final\_Acceptance\_Report.txt 最终验收报告

\- 增强 manifest.json 版本追踪

\- 增强 validation\_report.txt 验收信息

\- 支持工程包静态最终验收



\### 验收结果



\- ZIP 必要文件检查通过

\- Alarm\_List.csv 检查通过

\- Step\_List.csv 检查通过

\- IO\_Mapping\_Enhanced.csv 检查通过

\- 变量交叉引用报告检查通过

\- 最终验收报告检查通过

\- manifest / validation\_report 检查通过

\- V0.6.4 工程质量增强通过



\### 当前稳定输出



\- output/AI\_Device\_Project\_Package\_V06.zip



\### 下一版本



V0.6.5：成品版网页界面整理 + 一键生成最终交付包

\## V0.6.5 - 已封版



封版时间：2026-05-08



\### 核心能力



\- 新增 app\_product.py 成品版网页操作台

\- 新增 start\_v065\_product\_console.bat 一键启动脚本

\- 页面只保留成品主流程

\- 支持输入整机中文需求

\- 支持 AI 解析多工站配置

\- 支持人工确认解析结果

\- 支持一键生成最终工程包 ZIP

\- 支持下载 V0.6.5 最终交付包

\- 已接入 V0.6.4 工程质量增强核心



\### 当前最终交付能力



\- 气缸动作 ST

\- 多工站 ST

\- 整机主流程 ST

\- HMI 变量清单

\- DUT 结构声明

\- 全局变量声明

\- IO 映射表

\- 增强 IO 映射表

\- 报警清单

\- 步骤清单

\- 变量交叉引用报告

\- Sysmac 导入说明

\- ST 质量报告

\- 最终验收报告

\- manifest 追踪清单

\- validation\_report 校验报告



\### 验收结果



\- 成品版网页流程跑通

\- 最终 ZIP 可生成

\- 最终 ZIP 可下载

\- V0.6.5 成品版操作台通过



\### 当前启动方式



```bat

streamlit run app\_product.py
## V0.7.0 - 已封版

封版时间：2026-05-08

### 版本名称

PLC数字工程师 V0.7.0 最终成品封装版

### 核心能力

- 成品版网页操作台 app_product.py
- 一键启动器 start_plc_digital_engineer_v070.bat
- 整机中文需求输入
- AI解析多工站配置
- 人工确认解析结果
- 一键生成最终工程包 ZIP
- 下载最终交付包
- 生成气缸动作 ST
- 生成多工站 ST
- 生成整机主流程 ST
- 生成 HMI 变量清单
- 生成 DUT 结构声明
- 生成全局变量声明
- 生成 IO 映射表
- 生成增强 IO 映射表
- 生成报警清单
- 生成步骤清单
- 生成变量交叉引用报告
- 生成 Sysmac Studio 导入说明
- 生成 ST 静态质量报告
- 生成最终验收报告
- 生成 manifest 追踪清单
- 生成 validation_report 校验报告
- 生成最终发布目录
- 生成最终发布包 PLC_Digital_Engineer_V070_Release.zip

### 验收结果

- app_product.py 语法检查通过
- 后端生成器检查通过
- 最终工程包 ZIP 检查通过
- 发布目录检查通过
- Release ZIP 检查通过
- V0.7.0 最终成品封装版验收通过

### 当前启动方式

```bat
streamlit run app_product.py

## V0.7.1 - 已封版

封版时间：2026-05-08

### 版本名称

PLC数字工程师 V0.7.1 伺服控制基础版

### 核心能力

- 新增 servo_ai_parser.py
- 新增 servo_generator.py
- 支持从中文需求中识别伺服轴
- 支持识别 X/Y/Z 等轴名称
- 支持识别伺服回零要求
- 支持识别点位表
- 支持识别速度、加速度
- 支持生成 00_Servo_DUT_Global_Generated.st
- 支持生成 05_Servo_Axis_Generated.st
- 支持生成 configs/axis_config.json
- 支持生成 Servo_Point_Table.csv
- 支持生成 Servo_HMI_Variable_List.csv
- 支持生成 Servo_Alarm_List.csv
- 支持生成 Servo_Debug_Guide.txt
- app_product.py 已接入 Axis Config 显示
- 最终 ZIP 已包含伺服控制基础交付物

### 验收结果

- 伺服 AI 解析测试通过
- 伺服轴数量识别通过
- 点位表识别通过
- 伺服 ST 文件生成通过
- Servo HMI 变量清单生成通过
- Servo 报警清单生成通过
- axis_config.json 生成通过
- manifest V0.7.1 信息写入通过
- app_product 页面接入检查通过
- V0.7.1 伺服控制基础版验收通过

### 当前新增交付文件

- 00_Servo_DUT_Global_Generated.st
- 05_Servo_Axis_Generated.st
- configs/axis_config.json
- Servo_Point_Table.csv
- Servo_HMI_Variable_List.csv
- Servo_Alarm_List.csv
- Servo_Debug_Guide.txt

### 注意事项

V0.7.1 生成的是伺服控制框架，不是最终可直接上机的完整运动控制程序。  
正式使用前需要 PLC 工程师在 Sysmac Studio 中绑定真实 Axis 轴对象，并接入 MC_Power、MC_Home、MC_MoveAbsolute、MC_Stop 等运动控制指令。

### 下一版本建议

V0.7.2：伺服 MC 功能块真实化 + 轴状态机增强
