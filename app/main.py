import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import auth, items
from app.core.config import settings
from app.db.session import engine
from app.middleware.logging_middleware import RequestLoggingMiddleware

# Garantir que os modelos sejam importados (para criação de tabelas no MVP)
from app.models import item as _item  # noqa: F401
from app.models.user import Base

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO))


def create_app() -> FastAPI:
    app = FastAPI(title="fastapi-crud-auth")

    # Middleware global (request-id + duration)
    app.add_middleware(RequestLoggingMiddleware)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.on_event("startup")
    def on_startup():
        # MVP: cria tabelas automaticamente (depois migra para Alembic)
        Base.metadata.create_all(bind=engine)

    app.include_router(auth.router)
    app.include_router(items.router)

    return app


app = create_app()