from collections.abc import Iterable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Case


class CaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count_all(self) -> int:
        result = await self.session.scalar(select(func.count(Case.id)))
        return int(result or 0)

    async def max_order(self) -> int:
        result = await self.session.scalar(select(func.max(Case.order)))
        return int(result or 0)

    async def list_all(self) -> list[Case]:
        result = await self.session.scalars(select(Case).order_by(Case.order, Case.id))
        return list(result)

    async def list_visible(self) -> list[Case]:
        result = await self.session.scalars(
            select(Case).where(Case.is_visible.is_(True)).order_by(Case.order, Case.id)
        )
        return list(result)

    async def get(self, case_id: int) -> Case | None:
        return await self.session.get(Case, case_id)

    async def add(self, data: dict) -> Case:
        if "order" not in data:
            data["order"] = await self.max_order() + 1
        case = Case(**data)
        self.session.add(case)
        await self.session.flush()
        return case

    async def update(self, case: Case, data: dict) -> Case:
        for key, value in data.items():
            setattr(case, key, value)
        await self.session.flush()
        return case

    async def delete(self, case: Case) -> None:
        await self.session.delete(case)
        await self.session.flush()

    async def reorder(self, ordered_ids: Iterable[int]) -> None:
        cases = {case.id: case for case in await self.list_all()}
        for index, case_id in enumerate(ordered_ids, start=1):
            if case_id in cases:
                cases[case_id].order = index
        await self.session.flush()

