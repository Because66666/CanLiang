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

<img src="https://github.com/user-attachments/assets/f0faf0bb-8b73-4db4-b106-9cb12dc0443c" alt="示例图片" width="100%">

## 系统要求

- Python 3.6+
- Node.js和npm（用于前端开发和构建）
- BetterGI已安装（用于获取日志文件）

## 快速开始

### 首次运行

只需运行项目根目录下的`run.py`脚本：

```bash
python run.py
```

首次运行时，脚本会自动执行以下操作：

1. 检测BetterGI安装路径
2. 配置Python虚拟环境
3. 安装后端依赖
4. 安装并构建前端环境
5. 启动后端和前端服务



### 后续运行

初始化完成后，再次运行时将跳过环境配置步骤，直接启动服务器。

```bash
python run.py
```

## 手动配置

如果自动检测BetterGI安装路径失败，您需要手动在`server/.env`文件中设置BetterGI的安装路径：

```
BETTERGI_PATH=您的BetterGI安装路径
```

## 项目结构

```
Analyse_bettergi_log/
├── run.py                 # 主运行脚本
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

### 分析指定日期的日志

```
GET /api/analyse?date=YYYYMMDD
```

参数：
- `date`: 日志日期，格式为YYYYMMDD

返回指定日期日志的分析结果，包括交互或拾取物品的统计信息。

## 使用方法

1. 启动应用后，通过浏览器访问 http://localhost:3000
2. 在Web界面上选择要分析的日志日期
3. 查看分析结果，包括交互物品的统计信息

## 故障排除

- 如果无法自动检测BetterGI安装路径，请手动在`server/.env`文件中设置
- 确保已安装Python和Node.js
- 检查防火墙设置，确保允许本地端口5000（后端）和3000（前端）的访问

## 开发者信息

作者: Because66666
版本: 1.1.0

## 许可证

本项目遵循Apache-2.0 License许可证。
