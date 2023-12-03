from fastapi import FastAPI
from .router._manage import router as manage_router

import multiprocessing

app = FastAPI()

app.include_router(manage_router, prefix="/manage", tags=["manage"])
