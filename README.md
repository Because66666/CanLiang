# 参量质变仪：BetterGI日志分析工具

## 项目介绍

参量质变仪：BetterGI日志分析工具 是一个用于分析BetterGI（Better Genshin Impact）日志文件的应用程序。该工具提供了直观的Web界面，帮助用户查看和分析BetterGI生成的日志信息，特别是关于游戏中交互和拾取物品的统计数据。

### 主要功能

- 自动检测BetterGI安装路径
- 分析BetterGI日志文件中的各类型事件
- 统计交互或拾取物品的出现次数
- 提供REST API接口进行日志分析
- 通过Web界面直观展示分析结果

### 界面截图

<img src="https://github.com/user-attachments/assets/a67d635f-0922-454f-89c2-08237a86699f" alt="示例图片" width="100%">


### 致谢提交PR的合作开发者
- [xiaocdeh](https://github.com/xiaocdeh)，提交了 https://github.com/Because66666/CanLiang/pull/2

### 致谢提交Issues的关注者
- [crazysmile-PhD](https://github.com/crazysmile-PhD)，提交了 https://github.com/Because66666/CanLiang/issues/4

## 系统要求

- Python 3.6+

## 快速开始

### 首次运行

只需运行项目根目录下的`lite_runner.py`脚本：

```bash
python lite_runner.py
```

首次运行时，脚本会自动执行以下操作：

1. 检测BetterGI安装路径
2. 配置Python虚拟环境
3. 安装后端依赖
4. 启动服务



### 后续运行

初始化完成后，再次运行时将跳过环境配置步骤，直接启动服务器。

```bash
python lite_runner.py
```

## 手动配置

如果自动检测BetterGI安装路径失败，您需要手动在`mini/.env`文件中设置BetterGI的安装路径：

```
BETTERGI_PATH=您的BetterGI安装路径
```

## 项目结构

```
Analyse_bettergi_log/
├── mini/                  # 新一代免npm环境的服务。已将前端静态导出。
│   ├── app.py            # Flask应用主文件
│   ├── static/           # 前端静态文件
│   ├── requirements.txt  # Python依赖列表
│   └── README.md         # 后端服务说明
├── lite_runner.py         # 现启动脚本
├── run.py                 # 前一代运行脚本
├── server/                # 后端服务
│   ├── app.py            # Flask应用主文件
│   ├── analyse.py        # 日志分析模块
│   ├── requirements.txt  # Python依赖列表
│   └── README.md         # 后端服务说明
└── website/              # 前端应用
    └── ...               # 前端相关文件
```

## API接口

### 获取日志列表

```
GET /api/LogList
```

返回所有可分析的日志文件列表。
参考响应：
```JSON
{
  "list": [
    "20250504",
    "20250503",
    "20250218"
  ]
}
```
约定：日期为从现在到以前日期排序。靠近现在的日期在列表中靠前。
**细节**：BGI的日志仅保留最近31个日志文件。过于远古的日志文件不会被保留，因此canliang无法统计以前的数据。

### 获取所有日志数据

```
GET /api/LogData
```

返回所有日志的分析数据，包括持续时间和物品统计信息。
参考响应：
```JSON
{
  "duration": {
    "日期": ["20250504", "20250503", "20250502"],
    "持续时间": [3600, 7200, 5400]
  },
  "item": {
    "物品名称": ["兽肉", "鸟蛋", "冰晶蝶"],
    "时间": ["14:30:00", "14:35:00", "14:40:00"],
    "日期": ["20250504", "20250504", "20250504"],
    "归属配置组": ["config1", "config1", "config2"]
  }
}
```
说明：
- duration: 包含日期列表和对应的持续时间（秒）
- item: 包含物品交互记录的详细信息，包括物品名称、时间、日期和所属配置组

## 使用方法

1. 启动应用后，通过浏览器访问 http://localhost:3000
2. 在Web界面上选择要分析的日志日期
3. 查看分析结果，包括交互物品的统计信息和持续时间统计

## 故障排除

- 如果无法自动检测BetterGI安装路径，请手动在`mini/.env`文件中设置
- 确保已安装Python
- 检查防火墙设置，确保允许本地端口3001的访问

## 开发者信息

作者: Because66666
README版本: 1.1.5

## 许可证

本项目遵循Apache-2.0 License许可证。
