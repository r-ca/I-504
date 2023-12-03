from fastapi import APIRouter

from .manage.job import router as job_router

router = APIRouter()

router.include_router(job_router, prefix="/job", tags=["job"])
