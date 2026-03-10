from typing import Optional
from pydantic import BaseModel, Field


class CaseBrief(BaseModel):
    id: int = Field(description="案例在 cncases/cases 系统中的内部 ID")
    case_id: str = Field(description="案号，如 (2023)京01民终1234号")
    case_name: str = Field(description="案件名称")
    court: str = Field(description="审理法院")
    case_type: str = Field(description="案件类型：民事/刑事/行政/etc")
    procedure: str = Field(description="审理程序：一审/二审/再审/etc")
    judgment_date: str = Field(description="裁判日期")
    cause: str = Field(description="案由")
    preview: str = Field(default="", description="搜索结果中的摘要预览")


class CaseDetail(CaseBrief):
    doc_id: str = Field(default="", description="原始文书链接/ID")
    public_date: str = Field(default="", description="公开日期")
    parties: str = Field(default="", description="当事人")
    legal_basis: str = Field(default="", description="法律依据")
    full_text: str = Field(default="", description="判决书全文（纯文本）")


class SearchRequest(BaseModel):
    query: str = Field(description="搜索关键词")
    offset: int = Field(default=0, ge=0, description="分页偏移量")
    limit: int = Field(default=20, ge=1, le=100, description="返回数量上限")


class SearchResponse(BaseModel):
    query: str
    total: int = Field(description="匹配总数")
    offset: int
    cases: list[CaseBrief]


class CaseSummary(BaseModel):
    case_id: str
    case_name: str
    court: str
    judgment_date: str
    parties: str
    cause: str
    facts: str = Field(description="案件事实摘要")
    争议焦点: str = Field(default="", alias="dispute_focus", description="争议焦点")
    court_opinion: str = Field(description="法院认定意见")
    judgment_result: str = Field(description="判决结果")
    legal_basis: str = Field(description="适用法律条文")


class CaseComparison(BaseModel):
    case_ids: list[int]
    similarities: list[str] = Field(description="相似之处")
    differences: list[str] = Field(description="不同之处")
    fact_comparison: str = Field(description="事实对比分析")
    judgment_comparison: str = Field(description="判决对比分析")
    legal_basis_comparison: str = Field(description="法律依据对比")


class CompareRequest(BaseModel):
    case_ids: list[int] = Field(min_length=2, max_length=5, description="要对比的案例 ID 列表")


class ExtractedRules(BaseModel):
    case_id: int
    case_name: str
    rules: list["RuleItem"] = Field(description="提取的裁判规则")


class RuleItem(BaseModel):
    rule: str = Field(description="裁判规则描述")
    legal_basis: str = Field(description="法律依据")
    context: str = Field(description="适用情境/条件")
    quote: str = Field(default="", description="原文引用")
