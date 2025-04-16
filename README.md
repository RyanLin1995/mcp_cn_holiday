# 中国节假日查询 MCP 服务

这是一个基于 MCP (Message Control Protocol) 的中国节假日查询服务，提供节假日和工作日的查询功能。数据来源于 [holiday-cn](https://github.com/NateScarlet/holiday-cn) 项目。

## 功能特点

- 支持查询指定日期是否为节假日
- 支持查询指定日期是否为工作日
- 自动缓存和更新节假日数据
- 异步处理，高效响应
- 使用 FastMCP 框架，易于集成

## 安装要求

- Python 3.7+
- aiohttp
- mcp
- Node.js (用于运行MCP Inspector)

## 安装方法

1. 克隆仓库：
```bash
git clone [repository-url]
cd mcp_holiday
```

2. 安装依赖：
```bash
pip install aiohttp mcp
```

3. 安装MCP Inspector工具（用于测试MCP服务）：
```bash
# 确保已安装Node.js
npm install -g @modelcontextprotocol/inspector
```

## 运行服务

1. 启动Holiday MCP服务：
```bash
python holiday_mcp_server.py
```

2. 使用MCP Inspector测试服务：
```bash
npx @modelcontextprotocol/inspector python holiday_mcp_server
```

这将启动MCP Inspector界面，您可以通过它来测试和调试Holiday MCP服务的各个接口。

### API 接口说明：

### 查询节假日

- 资源：`date://is_holiday/{date}`
- 参数：
  - `date`: 日期字符串（格式：YYYY-MM-DD），可选，默认为当前日期
- 返回值：
  - `true`: 是节假日
  - `false`: 不是节假日
- 异常：
  - `ValueError`: 日期格式错误
  - `Exception`: 获取节假日数据失败

### 查询工作日

- 资源：`date://is_workday/{date}`
- 参数：
  - `date`: 日期字符串（格式：YYYY-MM-DD），可选，默认为当前日期
- 返回值：
  - `true`: 是工作日
  - `false`: 不是工作日
- 异常：
  - `ValueError`: 日期格式错误
  - `Exception`: 获取节假日数据失败

### 获取日期详细信息

- 资源：`date://get_holiday_info/{date}`
- 参数：
  - `date`: 日期字符串（格式：YYYY-MM-DD），可选，默认为当前日期
- 返回值：包含以下字段的JSON对象
  - `date`: 查询的日期
  - `is_holiday`: 是否为节假日
  - `is_workday`: 是否为工作日
  - `weekday`: 星期几（0-6，0表示周一）
  - `weekday_name`: 星期几的中文名称（如"周一"）
- 异常：
  - `ValueError`: 日期格式错误
  - `Exception`: 获取节假日数据失败

## 数据缓存

- 节假日数据会被缓存在 `holiday_data/holiday_data.json` 文件中
- 每年自动更新一次数据
- 如果缓存文件损坏或读取失败，会自动重新下载

## 贡献指南

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详细信息

## 致谢

- [holiday-cn](https://github.com/NateScarlet/holiday-cn) - 节假日数据来源
- [FastMCP](https://github.com/MCP-Foundation/FastMCP) - MCP 服务框架