from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
)

from db import db_helper

from schemas.skill import SkillCreate, SkillShortRead

from crud_repositories.skill import (
    create_skill,
    get_all_skills,
)

from service.skills import (
    delete_skill_service,
    update_skill_name_service,
    get_skill_by_id_service,
    get_skill_by_name_service,
)

router = APIRouter(tags=["Skills"])


@router.post("/skills/", response_model=SkillShortRead)
async def skill_create(
    creating_skill: SkillCreate,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    return await create_skill(session=session, creating_skill=creating_skill)


@router.get("/skills/", response_model=list[SkillShortRead])
async def get_skills(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    return await get_all_skills(session)


@router.get("/skills/{skill_id}/", response_model=SkillShortRead)
async def get_skill(
    skill_id: int,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    return await get_skill_by_id_service(session=session, skill_id=skill_id)


@router.get("/skills/by-name/{skill_name}", response_model=SkillShortRead)
async def get_skill(
    skill_name: str,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    return await get_skill_by_name_service(session=session, skill_name=skill_name)


@router.patch("/skills/{skill_id}", response_model=SkillShortRead)
async def update_skill_name(
    skill_id: int,
    new_skill_name: str,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    return await update_skill_name_service(
        skill_id=skill_id,
        new_skill_name=new_skill_name,
        session=session,
    )


@router.delete("/skills/{skill_id}")
async def delete_by_id(
    skill_id: int,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    await delete_skill_service(
        skill_id=skill_id,
        session=session,
    )
    return {"message": "Skill deleted successfully."}
