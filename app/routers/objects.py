from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projects import Project as ProjectModel
from app.models.objects import Object as ObjectModel
from app.schemas import Object as ObjectSchema, ObjectCreate
from app.db_depends import get_async_db

router = APIRouter(prefix='/objects', tags=['objects'])


@router.get('/', response_model=list[ObjectSchema])
async def get_all_objects(db: AsyncSession = Depends(get_async_db)):
    stmt = select(ObjectModel).where(ObjectModel.on_sale == True)
    result = await db.scalars(stmt)
    db_objects = result.all()
    return db_objects


@router.get("/project/{project_id}", response_model=list[ObjectSchema])
async def get_objects_by_project(project_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список активных товаров в указанной категории по её ID.
    """
    # Проверяем, существует ли активная категория
    result = await db.scalars(
        select(ProjectModel).where(ProjectModel.id == project_id,
                                   ProjectModel.is_active == True))
    db_project = result.first()

    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Category not found or inactive")

    # Получаем активные товары в категории
    result = await db.scalars(
        select(ObjectModel).where(ObjectModel.project_id == project_id,
                                  ObjectModel.on_sale == True))
    db_objects = result.all()
    return db_objects


@router.get("/{object_id}", response_model=ObjectSchema)
async def get_object(object_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(ObjectModel).where(ObjectModel.id == object_id, ObjectModel.on_sale == True)
    result = await db.scalars(stmt)
    db_object = result.first()

    if not db_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Object not found")

    # Проверяем, существует ли активный проект
    res = await db.scalars(
        select(ProjectModel).where(ProjectModel.id == db_object.project_id,
                                   ProjectModel.is_active == True))
    db_project = res.first()
    if not db_project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Project not found or inactive")

    return db_object


@router.post("/", response_model=ObjectSchema, status_code=status.HTTP_201_CREATED)
async def create_product(new_object: ObjectCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт новый товар.
    """
    # Проверяем, существует ли активный проект
    result = await db.scalars(
        select(ProjectModel).where(ProjectModel.id == new_object.project_id,
                                   ProjectModel.is_active == True))
    db_project = result.first()
    if not db_project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Project not found or inactive")

    # Создаём товар
    db_object = ObjectModel(**new_object.model_dump())
    db.add(db_object)
    await db.commit()
    await db.refresh(db_object)
    return db_object


@router.put("/{object_id}", response_model=ObjectSchema)
async def update_object(object_id: int, new_object: ObjectCreate, db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(
        select(ObjectModel).where(ObjectModel.id == object_id, ObjectModel.on_sale == True))
    db_object = result.first()

    if not db_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Object not found")

    # Проверяем, существует ли активный проект
    project = await db.scalars(
        select(ProjectModel).where(ProjectModel.id == new_object.project_id,
                                   ProjectModel.is_active == True))
    db_project = project.first()

    if not db_project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Project not found or inactive")

    await db.execute(
        update(ObjectModel).
        where(ObjectModel.id == object_id).
        values(**new_object.model_dump())
    )
    await db.commit()
    await db.refresh(db_object)
    return db_object


@router.delete("/{object_id}", response_model=ObjectSchema, status_code=status.HTTP_200_OK)
async def delete_object(object_id: int, db: AsyncSession = Depends(get_async_db)):
    object_result = await db.scalars(
        select(ObjectModel).where(ObjectModel.id == object_id, ObjectModel.on_sale == True))
    db_object = object_result.first()

    if not db_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Object not found or inactive")
    db_object.on_sale = False
    await db.commit()
    await db.refresh(db_object)
    return db_object


@router.delete("/")
async def delete_all_objects(db: AsyncSession = Depends(get_async_db)) -> dict:
    stmt = select(ObjectModel).where(ObjectModel.on_sale == True)
    result = await db.scalars(stmt)
    db_objects = result.all()

    for obj in db_objects:
        await db.execute(
            update(ObjectModel).where(ObjectModel.id == obj.id).values(on_sale=False))

    await db.commit()
    return {"status": "success", "message": "Objects were deleted"}
