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

<img src="https://github.com/user-attachments/assets/56430317-2614-4e99-adf0-96c8adcf6f7f" alt="示例图片" width="100%">

### 致谢提交PR的合作开发者
[xiaocdeh](https://github.com/xiaocdeh)，提交了 https://github.com/Because66666/CanLiang/pull/2  

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
### 分析指定日期的日志

```
GET /api/analyse?date=YYYYMMDD
```

参数：
- `date`: 日志日期，格式为YYYYMMDD
参考请求：http://xxx.xxx.xxx.xxx:5000/api/analyse?date=20250504

参考响应：
```JSON 
{
  "item_count": {
    "\u517d\u8089": 2,
    "\u51b0\u6676\u8776": 1,
    "\u6c61\u79fd\u7684\u9762\u5177": 16,
    "\u6c89\u91cd\u53f7\u89d2": 7,
    "\u6df7\u6c8c\u56de\u8def": 1,
    "\u7981\u5492\u7ed8\u5377": 4,
    "\u79bd\u8089": 2,
    "\u7ed3\u5b9e\u7684\u9aa8\u7247": 1,
    "\u8106\u5f31\u7684\u9aa8\u7247": 1,
    "\u8309\u6d01\u8349": 3,
    "\u987b\u5f25\u8537\u8587": 1,
    "\u9e1f\u86cb": 2,
    "\u9ec4\u91d1\u87f9": 1,
    "\u9ed1\u6676\u53f7\u89d2": 1,
    "\u9ed1\u94dc\u53f7\u89d2": 3
  },
  "duration": "6小时29分钟"
}
```
说明：
返回指定日期日志的分析结果，包括交互或拾取物品的统计信息。键为物品名称，值为该物品出现的次数。duration字段为总的运行时间计算。

## 使用方法

1. 启动应用后，通过浏览器访问 http://localhost:5000
2. 在Web界面上选择要分析的日志日期
3. 查看分析结果，包括交互物品的统计信息

## 故障排除

- 如果无法自动检测BetterGI安装路径，请手动在`mini/.env`文件中设置
- 确保已安装Python
- 检查防火墙设置，确保允许本地端口5000的访问

## 开发者信息

作者: Because66666
版本: 1.1.2

## 许可证

本项目遵循Apache-2.0 License许可证。
