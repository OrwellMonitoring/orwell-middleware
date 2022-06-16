from fastapi import APIRouter, HTTPException

from ..perfsonar.perfsonar_wrapper import PerfsonarMiddleware
from app.data.schemas.response import ErrorResponse


router = APIRouter()

@router.post("/perfsonar", tags=["perfsonar"])
async def add_perfsonar_node(address: str, label: str = None):
  if PerfsonarMiddleware.add_node(address, label):
    return ''
  raise HTTPException(status_code=400, detail=dict(ErrorResponse(error="Could not add host " + address, code=400)))
