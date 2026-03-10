from abc import ABC, abstractmethod

from app.schemas.case import CaseBrief, CaseDetail


class BaseCaseAdapter(ABC):
    @abstractmethod
    async def search(self, query: str, offset: int = 0, limit: int = 20) -> tuple[int, list[CaseBrief]]:
        ...

    @abstractmethod
    async def get_case(self, case_id: int) -> CaseDetail | None:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...
