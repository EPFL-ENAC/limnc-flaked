from typing import List
from fastapi import APIRouter, HTTPException
from ..services.config import config_service
from ..services.scheduler import scheduler_service
from ..models.domain import Config, InstrumentConfig
import os
cwd = os.getcwd()
router = APIRouter()


@router.get("/", response_model_exclude_none=True)
async def get_config() -> Config:
    """Get the system configuration

    Returns:
        Config: The general and the instruments configurations
    """
    return config_service.get_config()


@router.get("/cwd")
async def get_config() -> dict:
    """Get the system configuration

    Returns:
        Config: The general and the instruments configurations
    """
    return {'dir': os.getcwd()}


@router.get("/instruments", response_model_exclude_none=True)
async def get_config() -> List[InstrumentConfig]:
    """Get the instrument configurations

    Returns:
        List[InstrumentConfig]: The instrument configurations
    """
    return config_service.get_config().instruments


@router.get("/instrument/{name}", response_model_exclude_none=True)
async def get_instrument_config(name: str) -> InstrumentConfig:
    """Get the instrument configuration

    Args:
        name (str): The instrument name

    Returns:
        InstrumentConfig: The instrument configuration
    """
    return config_service.get_instrument_config(name)


@router.delete("/instrument/{name}", response_model_exclude_none=True)
async def get_instrument_config(name: str) -> InstrumentConfig:
    """Delete an instrument configuration and stop associated job

    Args:
        name (str): The instrument name

    Returns:
        InstrumentConfig: The deleted instrument configuration
    """
    config = config_service.get_instrument_config(name)
    if scheduler_service.has_job(name):
        scheduler_service.stop_job(name)
    config_service.delete_instrument_config(name)
    return config


@router.post("/instruments", response_model_exclude_none=True)
async def add_or_update_instrument_config(config: InstrumentConfig) -> InstrumentConfig:
    """Add or update an instrument configuration

    Args:
        config (InstrumentConfig): The instrument configuration

    Returns:
        InstrumentConfig: The instrument configuration
    """
    config_service.add_or_update_instrument_config(config)
    return config_service.get_instrument_config(config.name)
