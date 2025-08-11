from fastapi import APIRouter

from .hello_world import router as hello_world_router
from .channels import router as channels_router
from .webhook import router as webhook_router

api_router = APIRouter(prefix="/api")
api_router.include_router(hello_world_router)
api_router.include_router(channels_router)
api_router.include_router(webhook_router)
