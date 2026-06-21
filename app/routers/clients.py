from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clients import Client as ClientModel
from app.schemas import Client as ClientSchema, ClientCreate
from app.db_depends import get_async_db


router = APIRouter(prefix='/clients', tags=['clients'])


@router.get('/', response_model=list[ClientSchema])
async def get_all_clients(db: AsyncSession = Depends(get_async_db)):
    stmt = select(ClientModel).where(ClientModel.is_active == True)
    result = await db.scalars(stmt)
    db_clients = result.all()
    return db_clients


@router.get('/{client_id}', response_model=ClientSchema)
async def get_client_by_deal(client_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список у клиента по его ID.
    """
    # Проверяем, существует ли активный клиент
    stmt = select(ClientModel).where(ClientModel.id == client_id, ClientModel.is_active == True)
    result = await db.scalars(stmt)
    db_client = result.first()

    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Client not found or inactive")
    return db_client


@router.post('/', response_model=ClientSchema, status_code=status.HTTP_201_CREATED)
async def create_client(new_client: ClientCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт нового клиента.
    """
    db_client = ClientModel(**new_client.model_dump())
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client


@router.put("/{client_id}", response_model=ClientSchema)
async def update_client(client_id: int, new_client: ClientCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет клиента.
    :param client_id:
    :param new_client:
    :param db:
    :return:
    """
    result = await db.scalars(
        select(ClientModel).where(ClientModel.id == client_id, ClientModel.is_active == True))
    db_client = result.first()

    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Client not found or inactive")

    await db.execute(
        update(ClientModel).
        where(ClientModel.id == client_id).
        values(**new_client.model_dump())
    )
    await db.commit()
    await db.refresh(db_client)
    return db_client


@router.delete("/{client_id}", response_model=ClientSchema, status_code=status.HTTP_200_OK)
async def delete_client(client_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(
        select(ClientModel).where(ClientModel.id == client_id, ClientModel.is_active == True))
    db_client = result.first()

    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Client not found or inactive")
    db_client.is_active = False
    await db.commit()
    await db.refresh(db_client)
    return db_client


@router.delete("/")
async def delete_all_clients(db: AsyncSession = Depends(get_async_db)) -> dict:
    stmt = select(ClientModel).where(ClientModel.is_active == True)
    result = await db.scalars(stmt)
    db_clients = result.all()

    for client in db_clients:
        await db.execute(
            update(ClientModel).where(ClientModel.id == client.id).values(is_active=False))

    await db.commit()
    return {"status": "success", "message": "Clients were deleted"}