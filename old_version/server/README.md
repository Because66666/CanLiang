# BetterGI 日志分析服务

这是一个基于Flask的Web服务，用于分析BetterGI的日志文件并以JSON格式返回分析结果。

## 功能特点

- 提供REST API接口分析BetterGI日志文件
- 统计日志中各类型的出现次数
- 统计交互或拾取物品的出现次数
- 支持自定义日志文件路径

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 上运行。

## API 使用说明

### 分析日志文件

**请求**:

```
GET /api/analyse?file_path=日志文件路径
```

**参数**:

- `file_path`: 日志文件的路径（可选，默认为 `D:\software\BetterGI\log\better-genshin-impact20250430.log`）

**响应**:

```json
{
  "type_count": {
    "日志类型1": 出现次数,
    "日志类型2": 出现次数,
    ...
  },
  "item_count": {
    "物品名称1": 出现次数,
    "物品名称2": 出现次数,
    ...
  }
}
```

**错误响应**:

```json
{
  "error": "错误信息"
}
```

## 示例

```
GET http://localhost:5000/api/analyse
```

将返回默认日志文件的分析结果。

```
GET http://localhost:5000/api/analyse?file_path=D:\path\to\your\log\file.log
```

将返回指定日志文件的分析结果。