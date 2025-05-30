# 参量质变仪：BetterGI日志分析工具

## 项目介绍

参量质变仪：BetterGI日志分析工具 是一个用于分析BetterGI（Better Genshin Impact）日志文件的应用程序。该工具提供了直观的Web界面，帮助用户查看和分析BetterGI生成的日志信息，特别是关于游戏中交互和拾取物品的统计数据。

### 主要功能

- 自动检测BetterGI安装路径
- 分析BetterGI日志文件中的各类型事件
- 统计交互或拾取物品的出现次数
- 提供REST API接口进行日志分析
- 通过Web界面直观展示分析结果

### EXE可执行文件的使用方法
1. 直接启动，会自动检测BetterGI安装路径。
2. 使用`--path=xxx`参数指定BetterGI安装路径。
3. 使用`--help`或者`-h`参数查看帮助信息。
举例：
```
.\Canliang.exe --path=D:\BetterGI
```

### 界面截图

<img src="https://github.com/user-attachments/assets/f0faf0bb-8b73-4db4-b106-9cb12dc0443c" alt="示例图片" width="100%">

## 系统要求

- Python 3.6+


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
- `date`: 日志日期，格式为YYYYMMDD，或者使用`all`获取所有日期的汇总数据
参考请求：http://xxx.xxx.xxx.xxx:3000/api/analyse?date=20250504

参考响应：
```JSON 
{
  "duration": "5小时30分钟",
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
  }
}
```
说明：
返回指定日期日志的分析结果，包括运行持续时间和交互或拾取物品的统计信息。键为物品名称，值为该物品出现的次数。

### 获取物品历史趋势

```
GET /api/item-trend?item=物品名称
```

参数：
- `item`: 物品名称

参考请求：http://xxx.xxx.xxx.xxx:3000/api/item-trend?item=兽肉

参考响应：
```JSON
{
  "data": {
    "20250504": 2,
    "20250503": 5,
    "20250218": 1
  }
}
```

说明：
返回指定物品在各个日期的拾取数量统计。键为日期，值为该日期拾取的数量。

### 获取每日运行时间趋势

```
GET /api/duration-trend
```

参考请求：http://xxx.xxx.xxx.xxx:3000/api/duration-trend

参考响应：
```JSON
{
  "data": {
    "20250504": 330,
    "20250503": 420,
    "20250218": 180
  }
}
```

说明：
返回每日BetterGI的运行时间（分钟）统计。键为日期，值为该日期的运行时间（分钟）。

### 获取每日物品总数趋势

```
GET /api/total-items-trend
```

参考请求：http://xxx.xxx.xxx.xxx:3000/api/total-items-trend

参考响应：
```JSON
{
  "data": {
    "20250504": 45,
    "20250503": 38,
    "20250218": 22
  }
}
```

说明：
返回每日拾取物品总数统计。键为日期，值为该日期拾取的物品总数。

## 使用方法

1. 启动应用后，通过浏览器访问 http://localhost:3000
2. 在Web界面上选择要分析的日志日期
3. 查看分析结果，包括交互物品的统计信息

## 故障排除

- 如果无法自动检测BetterGI安装路径，请使用命令行参数`--bgi_path`指定路径
- 确保已安装Python
- 检查防火墙设置，确保允许本地端口3000的访问
- 如需更改端口，可使用命令行参数`--port`指定

## 开发者信息

作者: Because66666
版本: 1.1.2

## 许可证

本项目遵循Apache-2.0 License许可证。
