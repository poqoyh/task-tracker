import asyncio

from sqlalchemy import select

from auth.hashing import hash_password
from db.db_helper import db_helper
from db.models import User
from db.models.user import UserRole

ADMIN_EMAIL = "admin@admin.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"


async def create_admin() -> None:
    async with db_helper.session_factory() as session:
        existing = await session.execute(
            select(User).where(User.username == ADMIN_USERNAME)
        )
        if existing.scalar_one_or_none() is not None:
            print(f"User '{ADMIN_USERNAME}' already exists, skipping.")
            return

        admin = User(
            email=ADMIN_EMAIL,
            username=ADMIN_USERNAME,
            hashed_password=hash_password(ADMIN_PASSWORD),
            role=UserRole.ADMIN,
        )
        session.add(admin)
        await session.commit()
        print(f"Admin user created: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")

    await db_helper.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin())
