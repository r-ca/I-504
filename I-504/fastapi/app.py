from fastapi import FastAPI
from .router._manage import router as manage_router
from .router.test import router as test_router

import multiprocessing

app = FastAPI()

app.include_router(test_router, prefix="/test", tags=["test"])
app.include_router(manage_router, prefix="/manage", tags=["manage"])
