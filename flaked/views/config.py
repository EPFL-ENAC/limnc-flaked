from typing import List
from fastapi import APIRouter
from ..services.config import config_service
from ..services.scheduler import scheduler_service
from ..services.log import log_service
from ..models.domain import Config, SystemConfig, InstrumentConfig
import os
cwd = os.getcwd()
router = APIRouter()


@router.put("/")
async def reload() -> Config:
    """Reload the configuration file, and restart the scheduler.

    Returns:
        Config: The configuration
    """
    scheduler_service.stop()
    config_service.load_config()
    scheduler_service.start()
    return config_service.get_config()


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
    # remove all jobs associated with this instrument
    for job in scheduler_service.get_jobs(name):
        scheduler_service.stop_job(job["id"])
    # clear the cached logger for this instrument
    log_service.clear(name)
    # delete the instrument configuration
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
    # add or update the instrument configuration
    config_service.add_or_update_instrument_config(config)
    # register (or refresh) the jobs for this instrument
    scheduler_service.add_job(config.name)
    # clear the cached logger for this instrument
    log_service.clear(config.name)
    return config_service.get_instrument_config(config.name)
