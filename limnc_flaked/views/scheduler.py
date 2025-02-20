from fastapi import APIRouter, Query, HTTPException
from ..services.scheduler import scheduler_service

router = APIRouter()

@router.get("/status")
async def get_status():
    return {"status": scheduler_service.get_status()}

@router.put("/status")
async def set_status(
    action: str = Query(..., description="Action to perform on the scheduler service: start, stop, pause, or resume.")
):
    if action == "start":
        scheduler_service.start()
    elif action == "stop":
        scheduler_service.stop()
    elif action == "pause":
        scheduler_service.pause()
    elif action == "resume":
        scheduler_service.resume()
    else:
        raise HTTPException(status_code=400, detail="Invalid action.")
    return {"status": scheduler_service.get_status()}

@router.get("/jobs")
async def get_status():
    return scheduler_service.get_jobs()