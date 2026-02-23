from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routes.images import router as image_router
from app.routes.stats import router as stats_router
from app.routes.web import router as web_router
from app.services.captioner import captioner_service
from app.utils.logger import configure_logging

configure_logging()

app = FastAPI(title="Image Processing Pipeline")

Base.metadata.create_all(bind=engine)
captioner_service.load()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(web_router)
app.include_router(image_router)
app.include_router(stats_router)
