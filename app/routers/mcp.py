import logging

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.case import CompareRequest, SearchRequest
from app.services.case_service import CaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp/v1", tags=["mcp"])


def get_case_service() -> CaseService:
    from app.main import app_state

    return app_state["case_service"]


TOOLS_MANIFEST = [
    {
        "name": "search_cases",
        "description": "搜索中国裁判文书。支持关键词搜索，可按案由、法院、当事人等检索。基于 cncases/cases 开源项目提供的检索能力。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
                "offset": {"type": "integer", "description": "分页偏移量", "default": 0},
                "limit": {"type": "integer", "description": "返回数量", "default": 20},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_case_detail",
        "description": "获取裁判文书详情，包含全文内容。传入案例的内部 ID（从搜索结果获得）。",
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {"type": "integer", "description": "案例内部 ID"},
            },
            "required": ["case_id"],
        },
    },
    {
        "name": "summarize_case",
        "description": "生成案例结构化摘要，提取案件事实、争议焦点、法院意见、判决结果和法律依据。",
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {"type": "integer", "description": "案例内部 ID"},
            },
            "required": ["case_id"],
        },
    },
    {
        "name": "compare_cases",
        "description": "对比多个案例的异同，分析事实差异、判决差异和法律依据差异。",
        "parameters": {
            "type": "object",
            "properties": {
                "case_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "要对比的案例 ID 列表（2-5 个）",
                },
            },
            "required": ["case_ids"],
        },
    },
    {
        "name": "extract_rules",
        "description": "从裁判文书中提取裁判规则，包括法院认定的法律规则、适用条件和法律依据。",
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {"type": "integer", "description": "案例内部 ID"},
            },
            "required": ["case_id"],
        },
    },
]


@router.get("/tools", summary="列出可用工具")
async def list_tools():
    return {"tools": TOOLS_MANIFEST}


@router.post("/tools/{tool_name}", summary="调用工具")
async def call_tool(
    tool_name: str,
    arguments: dict,
    service: CaseService = Depends(get_case_service),
):
    try:
        if tool_name == "search_cases":
            request = SearchRequest(
                query=arguments["query"],
                offset=arguments.get("offset", 0),
                limit=arguments.get("limit", 20),
            )
            result = await service.search_cases(request)
            return {"result": result.model_dump()}

        elif tool_name == "get_case_detail":
            result = await service.get_case_detail(arguments["case_id"])
            if not result:
                raise HTTPException(status_code=404, detail="Case not found")
            return {"result": result.model_dump()}

        elif tool_name == "summarize_case":
            result = await service.summarize_case(arguments["case_id"])
            if not result:
                raise HTTPException(status_code=404, detail="Case not found")
            return {"result": result.model_dump()}

        elif tool_name == "compare_cases":
            request = CompareRequest(case_ids=arguments["case_ids"])
            result = await service.compare_cases(request)
            return {"result": result.model_dump()}

        elif tool_name == "extract_rules":
            result = await service.extract_rules(arguments["case_id"])
            if not result:
                raise HTTPException(status_code=404, detail="Case not found")
            return {"result": result.model_dump()}

        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required argument: {e}")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
