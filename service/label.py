from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession

from crud_repositories.label import (
    create_label,
    get_label_by_id,
    get_labels,
    count_labels,
    update_label,
    delete_label,
    label_has_task,
)

from schemas.pagination import PaginatedResponse

from schemas.label import (
    LabelCreate,
    LabelUpdate,
    LabelRead,
)


async def create_label_service(
    session: AsyncSession,
    creating_label: LabelCreate,
):
    try:
        return await create_label(session=session, creating_label=creating_label)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="Label with this name is already create"
        )


async def get_labels_service(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> PaginatedResponse[LabelRead]:

    items = await get_labels(
        session=session,
        limit=limit,
        offset=offset,
    )

    total = await count_labels(session=session)

    return PaginatedResponse[LabelRead](
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


async def get_label_by_id_service(
    session: AsyncSession,
    label_id: int,
):

    label = await get_label_by_id(session=session, label_id=label_id)

    if label is None:
        raise HTTPException(
            status_code=404,
            detail="Label not found",
        )

    return label


async def update_label_service(
    session: AsyncSession,
    label_id: int,
    update_data: LabelUpdate,
):

    label = await get_label_by_id_service(session=session, label_id=label_id)

    update_data = update_data.model_dump(exclude_unset=True)

    try:
        return await update_label(
            session=session,
            label=label,
            update_data=update_data,
        )
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Label with this name already exists",
        )


async def delete_label_service(
    session: AsyncSession,
    label_id: int,
):
    if await label_has_task(session=session, label_id=label_id):
        raise HTTPException(
            status_code=409,
            detail="Label has tasks, cannot delete",
        )

    label = await get_label_by_id_service(session=session, label_id=label_id)
    await delete_label(session=session, label=label)
