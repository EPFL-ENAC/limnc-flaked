from fastapi import APIRouter, Query, HTTPException
from ..services.scheduler import scheduler_service
from ..services.config import config_service
from ..models.query import Status, Action

router = APIRouter()


@router.get("/status")
async def get_status():
    """Get the status of the scheduler

    Returns:
        Status: The status of the scheduler
    """
    return Status(status=scheduler_service.get_status())


@router.put("/status")
async def set_status(
    action: Action = Query(
        ..., description="Action to perform on the scheduler service: start, stop, pause, or resume.")
) -> Status:
    """Set the status of the scheduler

    Args:
        action (Action, optional): Action to perform on the scheduler service: start, stop, pause, or resume.

    Returns:
        Status: The status of the scheduler
    """
    if action == Action.start:
        scheduler_service.start()
    elif action == Action.stop:
        scheduler_service.stop()
    elif action == Action.pause:
        scheduler_service.pause()
    elif action == Action.resume:
        scheduler_service.resume()
    return Status(status=scheduler_service.get_status())


@router.get("/jobs")
async def get_jobs() -> list:
    """Get the scheduler jobs

    Returns:
        list: The list of jobs
    """
    return scheduler_service.get_jobs()


@router.get("/job/{job_id}")
async def get_job(job_id: str) -> dict:
    """Get a job by identifier

    Args:
        job_id (str): The job identifier (instrument name)

    Raises:
        HTTPException: If the instrument or job is not found

    Returns:
        dict: The job information
    """
    if config_service.get_instrument_config(scheduler_service.get_instrument_name(job_id)) is None:
        raise HTTPException(status_code=404, detail="Instrument not found.")
    job = scheduler_service.get_job(job_id)
    if job is not None:
        return job
    raise HTTPException(status_code=404, detail="Job not found.")


@router.get("/job/{job_id}/status")
async def get_job_status(job_id: str) -> Status:
    """Get the status of a job

    Args:
        job_id (str): The job identifier (instrument name)

    Raises:
        HTTPException: If the instrument is not found

    Returns:
        Status: The job status
    """
    if config_service.get_instrument_config(scheduler_service.get_instrument_name(job_id)) is None:
        raise HTTPException(status_code=404, detail="Instrument not found.")
    if not scheduler_service.has_job(job_id):
        return Status(status="stopped")
    job = scheduler_service.get_job(job_id)
    if job["next_run_time"] == "None":
        return Status(status="paused")
    return Status(status="running")


@router.post("/job/{job_id}")
async def run_job(
    job_id: str,
) -> Status:
    if config_service.get_instrument_config(scheduler_service.get_instrument_name(job_id)) is None:
        raise HTTPException(status_code=404, detail="Instrument not found.")
    scheduler_service.run_job(job_id)
    return await get_job_status(job_id)


@router.put("/job/{job_id}/status")
async def set_job_status(
    job_id: str,
    action: Action = Query(
        ..., description="Action to perform on the scheduler service: start, stop, pause, or resume.")
) -> Status:
    if config_service.get_instrument_config(scheduler_service.get_instrument_name(job_id)) is None:
        raise HTTPException(status_code=404, detail="Instrument not found.")
    if action == Action.start:
        scheduler_service.start_job(job_id)
    else:
        if not scheduler_service.has_job(job_id):
            raise HTTPException(status_code=404, detail="Job not found.")
        if action == Action.stop:
            scheduler_service.stop_job(job_id)
        elif action == Action.pause:
            scheduler_service.pause_job(job_id)
        elif action == Action.resume:
            scheduler_service.resume_job(job_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid action.")
    return await get_job_status(job_id)
