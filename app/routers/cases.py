import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas.case import (
    CaseComparison,
    CaseDetail,
    CaseSummary,
    CompareRequest,
    ExtractedRules,
    SearchRequest,
    SearchResponse,
)
from app.services.case_service import CaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["cases"])


def get_case_service() -> CaseService:
    from app.main import app_state

    return app_state["case_service"]


@router.get("/search", response_model=SearchResponse, summary="搜索案例")
async def search_cases(
    query: str = Query(..., description="搜索关键词"),
    offset: int = Query(0, ge=0, description="分页偏移量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    service: CaseService = Depends(get_case_service),
):
    request = SearchRequest(query=query, offset=offset, limit=limit)
    return await service.search_cases(request)


@router.get("/cases/{case_id}", response_model=CaseDetail, summary="获取案例详情")
async def get_case_detail(
    case_id: int,
    service: CaseService = Depends(get_case_service),
):
    result = await service.get_case_detail(case_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return result


@router.get("/cases/{case_id}/summary", response_model=CaseSummary, summary="案例摘要")
async def summarize_case(
    case_id: int,
    service: CaseService = Depends(get_case_service),
):
    result = await service.summarize_case(case_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return result


@router.post("/compare", response_model=CaseComparison, summary="案例对比")
async def compare_cases(
    request: CompareRequest,
    service: CaseService = Depends(get_case_service),
):
    try:
        return await service.compare_cases(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/cases/{case_id}/rules", response_model=ExtractedRules, summary="提取裁判规则")
async def extract_rules(
    case_id: int,
    service: CaseService = Depends(get_case_service),
):
    result = await service.extract_rules(case_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return result
