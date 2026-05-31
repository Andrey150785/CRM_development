from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import AsyncSession

from app.models.projects import Project as ProjectModel
from app.schemas import Project as ProjectSchema, ProjectCreate
from app.db_depends import get_async_db


router = APIRouter(prefix='/deals', tags=['deals'])


@router.get('/', response_model=list[DealSchema])
def get_deals(db: AsyncSession = Depends(get_async_db)):
    pass


@router.get("/{deal_id}")
async def read_deal(deal_id: int) -> str:
    pass


@router.post('/', response_model=DealSchema, status_code=status.HTTP_201_CREATED)
async def create_deal(deal: DealCreate, db: AsyncSession = Depends(get_async_db)):
    pass


@router.put("/{deal_id}")
async def update_deal(deal_id: int, deal: str) -> str:
    pass


@router.delete("/{deal_id}")
async def delete_deal(deal_id: int) -> str:
    pass


@router.delete("/")
async def delete_deals() -> str:
    pass
