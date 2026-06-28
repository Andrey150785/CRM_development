from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, update, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deals import Deal as DealModel
from app.models.users import User as UserModel
from app.schemas import Deal as DealSchema, DealCreate, DealList
from app.db_depends import get_async_db

from app.auth import get_current_user

router = APIRouter(prefix='/deals', tags=['deals'])


@router.get('/', response_model=DealList)
async def get_all_deals(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список активных сделок в соответствии с указанными параметрами пагинации.
    :param page:
    :param page_size:
    :param db:
    :return:
    """
    total_stmt = select(func.count()).select_from(DealModel).where(DealModel.is_completed == False,
                                                                   DealModel.status != "canceled")
    total_count = await db.scalar(total_stmt) or 0

    deal_stmt = (select(DealModel).where(DealModel.is_completed == False, DealModel.status != "canceled")
                 .order_by(DealModel.id).offset((page - 1) * page_size).limit(page_size))
    result = await db.scalars(deal_stmt)
    db_deals = result.all()
    return {
        "deals": db_deals,
        "total": total_count,
        "page": page,
        "page_size": page_size
    }


@router.get("/user/{user_id}", response_model=list[DealSchema])
async def get_deals_by_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список активных товаров в указанной категории по её ID.
    """
    # Проверяем, существует ли активный пользователь
    result = await db.scalars(
        select(UserModel).where(UserModel.id == user_id,
                                UserModel.is_active == True))
    db_user = result.first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found or inactive")

    # Получаем активные сделки пользователя
    result = await db.scalars(
        select(DealModel).where(DealModel.user_id == user_id,
                                DealModel.is_completed == False, DealModel.status != "canceled"))
    db_deals = result.all()
    return db_deals


@router.get("/{deal_id}", response_model=DealSchema)
async def get_object(deal_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(DealModel).where(DealModel.id == deal_id, DealModel.is_completed == False,
                                   DealModel.status != "canceled")
    result = await db.scalars(stmt)
    db_deal = result.first()

    if not db_deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Deal not found")

    # Проверяем, существует ли активный пользователь
    res = await db.scalars(
        select(UserModel).where(DealModel.id == db_deal.user_id))
    db_user = res.first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User not found or inactive")

    return db_deal


@router.post("/", response_model=DealSchema, status_code=status.HTTP_201_CREATED)
async def create_deal(new_deal: DealCreate, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_user)):
    """
    Создаёт новую сделку, привязанную к активному пользователю.
    """
    # Проверяем, существует ли активный пользователь
    result = await db.scalars(
        select(UserModel).where(UserModel.id == current_user.id,
                                UserModel.is_active == True))
    db_user = result.first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User not found or inactive")

    # Создаём сделку
    db_deal = DealModel(**new_deal.model_dump(), user_id=current_user.id)
    db.add(db_deal)
    await db.commit()
    await db.refresh(db_deal)
    return db_deal


@router.put("/{deal_id}", response_model=DealSchema)
async def update_deal(deal_id: int, new_deal: DealCreate, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_user)):
    """
    Обновляет сделку, привязанную к активному пользователю.
    """
    result = await db.scalars(
        select(DealModel).where(DealModel.id == deal_id, DealModel.is_completed == False,
                                DealModel.status != "canceled"))
    db_deal = result.first()

    if not db_deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Deal not found or inactive")

    # Проверяем, существует ли активный пользователь
    if db_deal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own deals")

    user = await db.scalars(
        select(UserModel).where(UserModel.id == new_deal.user_id, UserModel.is_active == True))
    db_user = user.first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User not found or inactive")

    await db.execute(
        update(DealModel).
        where(DealModel.id == deal_id).
        values(**new_deal.model_dump())
    )
    await db.commit()
    await db.refresh(db_deal)
    return db_deal


@router.delete("/{deal_id}", response_model=DealSchema)
async def delete_deal(deal_id: int, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_user)):
    """
    Удаляет сделку, привязанную к активному пользователю.
    :param deal_id:
    :param db:
    :param current_user:
    :return:
    """
    deal_result = await db.scalars(
        select(DealModel).where(DealModel.id == deal_id, DealModel.is_completed == False,
                                DealModel.status != "canceled"))
    db_deal = deal_result.first()

    if not db_deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Deal not found or inactive")

    # Проверяем, существует ли активный пользователь
    if db_deal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own deals")

    await db.execute(update(DealModel).where(DealModel.id == deal_id).values(is_completed=True, status="canceled"))
    await db.commit()
    await db.refresh(db_deal)
    return db_deal


@router.delete("/")
async def delete_all_deals(db: AsyncSession = Depends(get_async_db)) -> dict:
    stmt = select(DealModel).where(DealModel.is_completed == False, DealModel.status != "canceled")
    result = await db.scalars(stmt)
    db_deals = result.all()

    for deal in db_deals:
        await db.execute(
            update(DealModel).where(DealModel.id == deal.id).values(is_completed=True, status="canceled"))

    await db.commit()
    return {"status": "success", "message": "Deals were deleted"}
