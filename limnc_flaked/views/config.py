from fastapi import APIRouter, HTTPException
from ..services.config import config_service

router = APIRouter()

@router.get("/")
async def get_config():
    return config_service.get_config()
