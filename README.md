# CaseLaw MCP Server

## 项目概述
法律案例检索与分析 FastAPI 服务，基于上游开源项目 [cncases/cases](https://github.com/cncases/cases) 提供的裁判文书检索能力，封装为 AI 可调用的工具层。

## 技术栈
- Python 3.11
- FastAPI + Uvicorn
- Pydantic v2 + pydantic-settings
- httpx (异步 HTTP 客户端)
- BeautifulSoup4 + lxml (HTML 解析)
- pytest + pytest-asyncio (测试)

## 架构
```
app/
├── main.py              # FastAPI 应用入口、生命周期管理
├── config.py            # 配置管理（环境变量）
├── adapters/            # 适配器层（策略模式）
│   ├── base.py          # 抽象基类
│   ├── caseopen.py      # 对接 cncases/cases 实例
│   └── mock.py          # 内置模拟数据
├── routers/             # API 路由
│   ├── cases.py         # REST API (/api/v1)
│   └── mcp.py           # MCP 工具接口 (/mcp/v1)
├── schemas/             # Pydantic 数据模型
│   └── case.py
├── services/            # 业务逻辑层
│   └── case_service.py  # 搜索、摘要、对比、规则提取
└── utils/
    └── logging.py       # 日志配置
```

## 五个核心工具
1. **search_cases** - 搜索裁判文书
2. **get_case_detail** - 获取案例详情
3. **summarize_case** - 生成结构化摘要
4. **compare_cases** - 多案例对比分析
5. **extract_rules** - 提取裁判规则

## 两种集成方式
- **A. CaseopenAdapter**: 直接对接自建 cncases/cases 实例（设置 `ADAPTER_TYPE=caseopen`）
- **B. MockAdapter**: 使用内置样例数据（默认，`ADAPTER_TYPE=mock`）

## 关键配置
- `ADAPTER_TYPE`: mock / caseopen
- `CASEOPEN_BASE_URL`: cncases/cases 实例地址
- `APP_PORT`: 5000
- `LOG_LEVEL`: INFO

## 运行方式
```bash
python run.py
```

## API 端点
- `GET /` - 服务状态
- `GET /health` - 健康检查
- `GET /docs` - Swagger 文档
- `GET /api/v1/search?query=合同` - 搜索
- `GET /api/v1/cases/{id}` - 案例详情
- `GET /api/v1/cases/{id}/summary` - 案例摘要
- `POST /api/v1/compare` - 案例对比
- `GET /api/v1/cases/{id}/rules` - 规则提取
- `GET /mcp/v1/tools` - MCP 工具清单
- `POST /mcp/v1/tools/{name}` - 调用 MCP 工具

## 测试
```bash
python -m pytest tests/ -v
```
