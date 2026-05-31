from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import AsyncSession

from app.models.projects import Project as ProjectModel
from app.schemas import Project as ProjectSchema, ProjectCreate
from app.db_depends import get_async_db


router = APIRouter(prefix='/clients', tags=['clients'])


@router.get('/', response_model=list[ClientSchema])
def get_clients(db: AsyncSession = Depends(get_async_db)):
    pass


@router.get("/{client_id}")
async def read_client(client_id: int) -> str:
    pass


@router.post('/', response_model=ClientSchema, status_code=status.HTTP_201_CREATED)
async def create_client(client: ClientCreate, db: AsyncSession = Depends(get_async_db)):
    pass


@router.put("/{client_id}")
async def update_client(client_id: int, client: str) -> str:
    pass


@router.delete("/{client_id}")
async def delete_client(client_id: int) -> str:
    pass


@router.delete("/")
async def delete_clients() -> str:
    pass
