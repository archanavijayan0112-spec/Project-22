from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import emissions, providers, recommendations, regions, upload
from app.core.config import get_settings
from app.db.database import init_db

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Estimate, compare, and reduce the carbon footprint of your cloud infrastructure.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix=settings.API_V1_PREFIX)
app.include_router(emissions.router, prefix=settings.API_V1_PREFIX)
app.include_router(regions.router, prefix=settings.API_V1_PREFIX)
app.include_router(providers.router, prefix=settings.API_V1_PREFIX)
app.include_router(recommendations.router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": settings.PROJECT_NAME}


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "healthy"}
