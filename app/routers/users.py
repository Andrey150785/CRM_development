from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.users import User as UserModel
from app.schemas import UserCreate, User as UserSchema
from app.db_depends import get_async_db
from app.auth import hash_password


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserSchema])
async def get_users(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех пользователей.
    """
    stmt = select(UserModel).where(UserModel.is_active == True)
    result = await db.scalars(stmt)
    db_users = result.all()
    return db_users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает пользователя по его ID.
    """
    stmt = select(UserModel).where(UserModel.id == user_id, UserModel.is_active == True)
    result = await db.scalars(stmt)
    db_user = result.first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return db_user


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Регистрирует нового пользователя с ролью 'reader' или 'admin'.
    """

    # Проверка уникальности email
    result = await db.scalars(select(UserModel).where(UserModel.email == user.email))
    if result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered")

    # Создание объекта пользователя с хешированным паролем
    db_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )

    # Добавление в сессию и сохранение в базе
    db.add(db_user)
    await db.commit()
    return db_user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(user_id: int, user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет данные пользователя по его ID.
    """
    result = await db.scalars(select(UserModel).where(UserModel.id == user_id, UserModel.is_active == True))
    db_user = result.first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    await db.execute(
        update(UserModel).
        where(UserModel.id == user_id).
        values(email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role))
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", response_model=UserSchema, status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Удаляет пользователя по его ID.
    """
    result = await db.scalars(select(UserModel).where(UserModel.id == user_id, UserModel.is_active == True))
    db_user = result.first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    db_user.is_active = False
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/")
async def delete_all_users(db: AsyncSession = Depends(get_async_db)) -> dict:
    stmt = select(UserModel).where(UserModel.is_active == True)
    result = await db.scalars(stmt)
    db_users = result.all()

    for user in db_users:
        await db.execute(
            update(UserModel).where(UserModel.id == user.id).values(is_active=False))
        await db.commit()
        await db.refresh(db_users)

    return {"status": "success", "message": "Users were deleted"}
