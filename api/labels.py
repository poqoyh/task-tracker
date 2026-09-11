from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from auth.dependencies import require_role
from db import db_helper
from db.models.user import UserRole, User
from schemas.pagination import PaginationParams, PaginatedResponse


from schemas.label import (
    LabelBase,
    LabelCreate,
    LabelUpdate,
    LabelRead,
)

from service.label import (
    create_label_service,
    get_labels_service,
    get_label_by_id_service,
    update_label_service,
    delete_label_service,
)

router = APIRouter(tags=["Labels"])


@router.post("/", response_model=LabelRead)
async def create_label(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    creating_label: LabelCreate,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await create_label_service(session=session, creating_label=creating_label)


@router.get("/", response_model=PaginatedResponse[LabelRead])
async def get_all_labels(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    pagination: Annotated[PaginationParams, Depends()],
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await get_labels_service(
        session=session,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get("/{label_id}/", response_model=LabelRead)
async def get_label_by_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    label_id: int,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await get_label_by_id_service(session=session, label_id=label_id)


@router.patch("/{skill_id}/", response_model=LabelRead)
async def update_label(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    label_id: int,
    update_data: LabelUpdate,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await update_label_service(
        session=session,
        label_id=label_id,
        update_data=update_data,
    )


@router.delete("/{label_id}/")
async def delete_label_by_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    label_id: int,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):

    await delete_label_service(
        session=session,
        label_id=label_id,
    )

    return {"message": "Label deleted successfully"}
