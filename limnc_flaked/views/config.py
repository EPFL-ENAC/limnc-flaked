from typing import List
from fastapi import APIRouter, HTTPException
from ..services.config import config_service
from ..models.domain import Config, InstrumentConfig

router = APIRouter()


@router.get("/", response_model_exclude_none=True)
async def get_config() -> Config:
    return config_service.get_config()


@router.get("/instruments", response_model_exclude_none=True)
async def get_config() -> List[InstrumentConfig]:
    return config_service.get_config().instruments


@router.get("/instrument/{name}", response_model_exclude_none=True)
async def get_instrument_config(name: str) -> InstrumentConfig:
    return config_service.get_instrument_config(name)
