import csv
import io
import logging
import re

import httpx
from bs4 import BeautifulSoup

from app.schemas.case import CaseBrief, CaseDetail

from .base import BaseCaseAdapter

logger = logging.getLogger(__name__)


class CaseopenAdapter(BaseCaseAdapter):
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "CaseLawMCP/1.0"},
        )

    async def search(self, query: str, offset: int = 0, limit: int = 20) -> tuple[int, list[CaseBrief]]:
        try:
            response = await self.client.get(
                "/",
                params={
                    "search": query,
                    "offset": offset,
                    "export": "true",
                },
            )
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "text/csv" in content_type or "application/octet-stream" in content_type:
                return self._parse_csv_results(response.text, offset, limit)

            return self._parse_html_search(response.text, offset, limit)
        except httpx.HTTPError as e:
            logger.error("Search request failed: %s", e)
            raise ConnectionError(f"Failed to connect to caseopen backend: {e}") from e

    def _parse_csv_results(self, csv_text: str, offset: int, limit: int) -> tuple[int, list[CaseBrief]]:
        cases = []
        reader = csv.DictReader(io.StringIO(csv_text))
        all_rows = list(reader)
        total = len(all_rows)

        for row in all_rows[offset : offset + limit]:
            try:
                case = CaseBrief(
                    id=int(row.get("id", 0)),
                    case_id=row.get("案号", ""),
                    case_name=row.get("案件名称", ""),
                    court=row.get("法院", ""),
                    case_type=row.get("案件类型", ""),
                    procedure=row.get("审理程序", ""),
                    judgment_date=row.get("裁判日期", ""),
                    cause=row.get("案由", ""),
                    preview=row.get("当事人", ""),
                )
                cases.append(case)
            except (ValueError, KeyError) as e:
                logger.warning("Skipping malformed CSV row: %s", e)
                continue

        return total, cases

    def _parse_html_search(self, html: str, offset: int, limit: int) -> tuple[int, list[CaseBrief]]:
        soup = BeautifulSoup(html, "lxml")
        cases = []

        total_match = re.search(r"找到\s*(\d+)", html)
        total = int(total_match.group(1)) if total_match else 0

        for result_div in soup.select(".search-result-text")[:limit]:
            try:
                link = result_div.select_one("a.nounderline")
                href = link.get("href", "") if link else ""
                id_match = re.search(r"/case/(\d+)", href)
                case_internal_id = int(id_match.group(1)) if id_match else 0

                title_el = result_div.select_one("h3")
                case_name = title_el.get_text(strip=True) if title_el else ""

                info_els = result_div.select("p.info")
                meta_text = info_els[0].get_text(strip=True) if info_els else ""
                meta_parts = [p.strip() for p in meta_text.split("-")]

                bottom_text = info_els[1].get_text(strip=True) if len(info_els) > 1 else ""
                bottom_parts = [p.strip() for p in bottom_text.split("-")]

                preview_el = result_div.select_one("p:not(.info)")
                preview = preview_el.get_text(strip=True) if preview_el else ""

                case = CaseBrief(
                    id=case_internal_id,
                    case_id=bottom_parts[0] if bottom_parts else "",
                    case_name=case_name,
                    court=bottom_parts[1] if len(bottom_parts) > 1 else "",
                    case_type=meta_parts[1] if len(meta_parts) > 1 else "",
                    procedure=meta_parts[2] if len(meta_parts) > 2 else "",
                    judgment_date=meta_parts[0] if meta_parts else "",
                    cause="",
                    preview=preview,
                )
                cases.append(case)
            except (IndexError, ValueError) as e:
                logger.warning("Skipping malformed HTML result: %s", e)
                continue

        return total, cases

    async def get_case(self, case_id: int) -> CaseDetail | None:
        try:
            response = await self.client.get(f"/case/{case_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return self._parse_case_html(case_id, response.text)
        except httpx.HTTPError as e:
            logger.error("Case detail request failed: %s", e)
            raise ConnectionError(f"Failed to fetch case {case_id}: {e}") from e

    def _parse_case_html(self, internal_id: int, html: str) -> CaseDetail:
        soup = BeautifulSoup(html, "lxml")

        def _meta(label: str) -> str:
            el = soup.find("td", string=re.compile(label))
            if el:
                val = el.find_next_sibling("td")
                return val.get_text(strip=True) if val else ""
            return ""

        full_text_div = soup.select_one(".case-content") or soup.select_one("main") or soup.select_one("body")
        full_text = full_text_div.get_text("\n", strip=True) if full_text_div else ""

        title_el = soup.select_one("h1") or soup.select_one("h2") or soup.select_one("title")
        case_name = title_el.get_text(strip=True) if title_el else ""

        return CaseDetail(
            id=internal_id,
            doc_id=_meta("原始链接"),
            case_id=_meta("案号") or _meta("案件编号"),
            case_name=case_name,
            court=_meta("法院"),
            case_type=_meta("案件类型"),
            procedure=_meta("审理程序"),
            judgment_date=_meta("裁判日期"),
            public_date=_meta("公开日期"),
            parties=_meta("当事人"),
            cause=_meta("案由"),
            legal_basis=_meta("法律依据"),
            full_text=full_text,
        )

    async def close(self) -> None:
        await self.client.aclose()
