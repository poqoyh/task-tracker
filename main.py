from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core.config import settings

from api import router as api_router
from db import db_helper

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from core.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
)
main_app.include_router(
    api_router,
    prefix=settings.api.api_prefix,
)

main_app.state.limiter = limiter
main_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
main_app.add_middleware(SlowAPIMiddleware)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
