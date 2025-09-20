from fastapi import APIRouter, HTTPException
from typing import List
from ..dependencies import get_availability_service
from ...services.availability import AvailabilityService
from ...db.schemas.table import TableAvailability

router = APIRouter()

@router.get("/availability", response_model=List[TableAvailability])
async def check_availability(time: str, party_size: int, service: AvailabilityService = get_availability_service()):
    """
    Check the availability of tables for a given time and party size.
    """
    availability = await service.get_availability(time, party_size)
    if not availability:
        raise HTTPException(status_code=404, detail="No tables available at this time")
    return availability