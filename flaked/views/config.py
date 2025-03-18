from typing import List
from fastapi import APIRouter
from ..services.config import config_service
from ..services.scheduler import scheduler_service
from ..services.log import log_service
from ..models.domain import SystemConfig, InstrumentConfig
import os
cwd = os.getcwd()
router = APIRouter()


@router.get("/settings", response_model_exclude_none=True)
async def get_settings() -> SystemConfig:
    """Get the system configuration

    Returns:
        SystemConfig: The system configuration
    """
    return config_service.get_config().settings


@router.get("/runtime")
async def get_runtime() -> dict:
    """Get some runtime information

    Returns:
        dict: The current working directory etc.
    """
    return {'cwd': os.getcwd(), 'config_path': config_service.config_file}


@router.get("/instruments", response_model_exclude_none=True)
async def get_instruments_config() -> List[InstrumentConfig]:
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
    log_service.clear(name)
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
    log_service.clear(config.name)
    return config_service.get_instrument_config(config.name)
