import logging
import re

from app.adapters.base import BaseCaseAdapter
from app.schemas.case import (
    CaseComparison,
    CaseDetail,
    CaseSummary,
    CompareRequest,
    ExtractedRules,
    RuleItem,
    SearchRequest,
    SearchResponse,
)

logger = logging.getLogger(__name__)


class CaseService:
    def __init__(self, adapter: BaseCaseAdapter):
        self.adapter = adapter

    async def search_cases(self, request: SearchRequest) -> SearchResponse:
        logger.info("Searching cases: query=%s offset=%d limit=%d", request.query, request.offset, request.limit)
        total, cases = await self.adapter.search(request.query, request.offset, request.limit)
        return SearchResponse(
            query=request.query,
            total=total,
            offset=request.offset,
            cases=cases,
        )

    async def get_case_detail(self, case_id: int) -> CaseDetail | None:
        logger.info("Fetching case detail: id=%d", case_id)
        return await self.adapter.get_case(case_id)

    async def summarize_case(self, case_id: int) -> CaseSummary | None:
        logger.info("Summarizing case: id=%d", case_id)
        case = await self.adapter.get_case(case_id)
        if not case:
            return None
        return self._extract_summary(case)

    async def compare_cases(self, request: CompareRequest) -> CaseComparison:
        logger.info("Comparing cases: ids=%s", request.case_ids)
        cases = []
        for cid in request.case_ids:
            case = await self.adapter.get_case(cid)
            if not case:
                raise ValueError(f"Case {cid} not found")
            cases.append(case)
        return self._build_comparison(cases)

    async def extract_rules(self, case_id: int) -> ExtractedRules | None:
        logger.info("Extracting rules: id=%d", case_id)
        case = await self.adapter.get_case(case_id)
        if not case:
            return None
        return self._extract_rules(case)

    def _extract_summary(self, case: CaseDetail) -> CaseSummary:
        text = case.full_text

        facts = self._extract_section(text, [
            r"经审理查明[：:](.*?)(?=本院认为|综上)",
            r"经查明[：:](.*?)(?=本院认为|综上)",
            r"查明[：:](.*?)(?=本院认为)",
        ])

        court_opinion = self._extract_section(text, [
            r"本院认为[：:](.*?)(?=判决如下|综上|依据)",
            r"本院认为[，,](.*?)(?=判决如下|综上)",
        ])

        judgment_result = self._extract_section(text, [
            r"判决如下[：:](.*?)(?=审判长|审判员|$)",
            r"裁定如下[：:](.*?)(?=审判长|审判员|$)",
        ])

        dispute_focus = self._extract_section(text, [
            r"争议焦点[：:](.*?)(?=\n|本院认为)",
            r"本案的焦点[：:](.*?)(?=\n|本院认为)",
        ])

        return CaseSummary(
            case_id=case.case_id,
            case_name=case.case_name,
            court=case.court,
            judgment_date=case.judgment_date,
            parties=case.parties,
            cause=case.cause,
            facts=facts or "（未能自动提取事实部分）",
            dispute_focus=dispute_focus or "",
            court_opinion=court_opinion or "（未能自动提取法院意见）",
            judgment_result=judgment_result or "（未能自动提取判决结果）",
            legal_basis=case.legal_basis,
        )

    def _extract_section(self, text: str, patterns: list[str]) -> str:
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()[:2000]
        return ""

    def _build_comparison(self, cases: list[CaseDetail]) -> CaseComparison:
        similarities = []
        differences = []

        case_types = set(c.case_type for c in cases)
        if len(case_types) == 1:
            similarities.append(f"案件类型相同：{case_types.pop()}")
        else:
            differences.append(f"案件类型不同：{', '.join(f'{c.case_name}({c.case_type})' for c in cases)}")

        causes = set(c.cause for c in cases)
        if len(causes) == 1:
            similarities.append(f"案由相同：{causes.pop()}")
        else:
            differences.append(f"案由不同：{', '.join(f'{c.case_name}({c.cause})' for c in cases)}")

        procedures = set(c.procedure for c in cases)
        if len(procedures) == 1:
            similarities.append(f"审理程序相同：{procedures.pop()}")
        else:
            differences.append(f"审理程序不同：{', '.join(f'{c.case_name}({c.procedure})' for c in cases)}")

        courts = set(c.court for c in cases)
        if len(courts) == 1:
            similarities.append(f"同一法院审理：{courts.pop()}")
        else:
            differences.append(f"不同法院审理：{', '.join(c.court for c in cases)}")

        basis_sets = [set(c.legal_basis.replace("，", ",").split(",")) for c in cases]
        common_basis = basis_sets[0]
        for bs in basis_sets[1:]:
            common_basis = common_basis & bs
        if common_basis:
            similarities.append(f"共同法律依据：{'、'.join(b.strip() for b in common_basis if b.strip())}")

        fact_parts = []
        judgment_parts = []
        for c in cases:
            facts = self._extract_section(c.full_text, [r"经审理查明[：:](.*?)(?=本院认为|综上)"])
            fact_parts.append(f"【{c.case_name}】{facts[:300] if facts else '未提取到事实部分'}")
            result = self._extract_section(c.full_text, [r"判决如下[：:](.*?)(?=审判长|$)"])
            judgment_parts.append(f"【{c.case_name}】{result[:300] if result else '未提取到判决部分'}")

        return CaseComparison(
            case_ids=[c.id for c in cases],
            similarities=similarities,
            differences=differences,
            fact_comparison="\n\n".join(fact_parts),
            judgment_comparison="\n\n".join(judgment_parts),
            legal_basis_comparison="\n".join(
                f"【{c.case_name}】{c.legal_basis}" for c in cases
            ),
        )

    def _extract_rules(self, case: CaseDetail) -> ExtractedRules:
        rules = []
        text = case.full_text

        opinion = self._extract_section(text, [
            r"本院认为[：:，,](.*?)(?=判决如下|裁定如下|综上)",
        ])

        if opinion:
            sentences = re.split(r"[。；]", opinion)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence or len(sentence) < 10:
                    continue

                legal_ref_match = re.search(
                    r"(依据|根据|依照|按照).*?(《.*?》.*?第.*?条)", sentence
                )
                legal_basis = legal_ref_match.group(2) if legal_ref_match else ""

                is_rule = any(
                    kw in sentence
                    for kw in ["应当", "构成", "属于", "不得", "依法", "违反", "符合", "认定"]
                )

                if is_rule or legal_basis:
                    rules.append(
                        RuleItem(
                            rule=sentence[:500],
                            legal_basis=legal_basis or case.legal_basis,
                            context=case.cause,
                            quote=sentence[:300],
                        )
                    )

        if not rules:
            rules.append(
                RuleItem(
                    rule=f"本案涉及{case.cause}，法院依据相关法律作出裁判",
                    legal_basis=case.legal_basis,
                    context=case.cause,
                    quote="",
                )
            )

        return ExtractedRules(
            case_id=case.id,
            case_name=case.case_name,
            rules=rules,
        )
