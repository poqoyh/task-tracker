from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Label, TaskLabel
from schemas.label import LabelCreate


async def create_label(
    session: AsyncSession,
    creating_label: LabelCreate,
) -> Label:

    label_data = creating_label.model_dump()

    label = Label(**label_data)

    session.add(label)
    await session.commit()
    await session.refresh(label)

    return label


async def get_label_by_id(
    session: AsyncSession,
    label_id: int,
) -> Label | None:
    stmt = select(Label).where(Label.id == label_id)

    result = await session.scalars(stmt)
    result = result.one_or_none()

    return result


async def get_labels(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> list[Label]:
    stmt = select(Label).order_by(Label.id).limit(limit).offset(offset)

    result = await session.scalars(stmt)

    return result.all()


async def count_labels(session: AsyncSession) -> int:
    result = await session.scalar(select(func.count()).select_from(Label))

    return result or 0


async def label_has_task(session: AsyncSession, label_id: int) -> bool:
    stmt = select(TaskLabel).where(TaskLabel.label_id == label_id).limit(1)

    result = await session.scalars(stmt)

    return result.first() is not None


async def update_label(
    session: AsyncSession,
    label: Label,
    update_data: dict,
) -> Label:

    for field, value in update_data.items():
        setattr(label, field, value)

    await session.commit()
    await session.refresh(label)

    return label


async def delete_label(session: AsyncSession, label: Label):
    await session.delete(label)
    await session.commit()
