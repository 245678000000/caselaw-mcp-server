import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.adapters.caseopen import CaseopenAdapter
from app.adapters.mock import MockAdapter
from app.config import settings
from app.routers import cases, mcp
from app.services.case_service import CaseService
from app.utils.logging import setup_logging

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

app_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CaseLaw MCP Server")
    logger.info("Adapter type: %s", settings.adapter_type)

    if settings.adapter_type == "caseopen":
        adapter = CaseopenAdapter(
            base_url=settings.caseopen_base_url,
            timeout=settings.request_timeout,
        )
        logger.info("Connected to caseopen backend: %s", settings.caseopen_base_url)
    else:
        adapter = MockAdapter()
        logger.info("Using mock adapter with sample data")

    service = CaseService(adapter)
    app_state["adapter"] = adapter
    app_state["case_service"] = service

    yield

    await adapter.close()
    logger.info("CaseLaw MCP Server stopped")


app = FastAPI(
    title="CaseLaw MCP Server",
    description=(
        "法律案例检索与分析服务，基于 cncases/cases 开源项目提供的裁判文书检索能力，"
        "提供 AI 可调用的工具层，包括案例搜索、详情查看、摘要生成、案例对比和裁判规则提取。"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(mcp.router)


@app.get("/", summary="服务状态")
async def root():
    return {
        "service": "CaseLaw MCP Server",
        "version": "0.1.0",
        "status": "running",
        "adapter": settings.adapter_type,
        "description": "法律案例检索与分析 AI 工具服务，基于 cncases/cases 上游项目",
        "docs_url": "/docs",
        "endpoints": {
            "rest_api": "/api/v1",
            "mcp_tools": "/mcp/v1/tools",
        },
    }


@app.get("/health", summary="健康检查")
async def health():
    return {"status": "healthy", "adapter": settings.adapter_type}


@app.exception_handler(ConnectionError)
async def connection_error_handler(request, exc):
    return JSONResponse(
        status_code=502,
        content={
            "detail": str(exc),
            "hint": "请检查 caseopen 后端服务是否运行，以及 CASEOPEN_BASE_URL 配置是否正确",
        },
    )
