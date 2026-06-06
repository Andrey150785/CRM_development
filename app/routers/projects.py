from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projects import Project as ProjectModel
from app.schemas import Project as ProjectSchema, ProjectCreate
from app.db_depends import get_async_db


router = APIRouter(prefix='/projects', tags=['projects'])


@router.get('/', response_model=list[ProjectSchema])
async def get_all_projects(db: AsyncSession = Depends(get_async_db)):
    stmt = select(ProjectModel).where(ProjectModel.is_active == True)
    result = await db.scalars(stmt)
    db_projects = result.all()
    return db_projects


@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(project_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(ProjectModel).where(ProjectModel.id == project_id, ProjectModel.is_active == True)
    result = await db.execute(stmt)
    db_project = result.scalars().first()

    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Project not found')
    return db_project


@router.post('/', response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_async_db)):
    if project.parent_id:
        stmt = select(ProjectModel).where(ProjectModel.id == project.parent_id,
                                          ProjectModel.is_active == True)
        result = await db.scalars(stmt)
        parent = result.first()
        if not parent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parent project not found')

    db_project = ProjectModel(**project.model_dump())
    db.add(db_project)
    await db.commit()
    return db_project


@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(project_id: int, project: ProjectCreate, db: AsyncSession = Depends(get_async_db)):
    stmt = select(ProjectModel).where(ProjectModel.id == project_id, ProjectModel.is_active == True)
    result = await db.scalars(stmt)
    db_project = result.first()

    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Project not found')

    if project.parent_id:
        parent_stmt = select(ProjectModel).where(ProjectModel.id == project.parent_id,
                                                 ProjectModel.is_active == True)
        result = await db.scalars(parent_stmt)
        parent = result.first()

        if not parent:
            raise HTTPException(status_code=400, detail='Parent project not found')

        if parent.id == project_id:
            raise HTTPException(status_code=400, detail='Parent project cannot be a child of itself')

    update_data = project.model_dump(exclude_unset=True)
    await db.execute(
        update(ProjectModel).
        where(ProjectModel.id == project_id).
        values(**update_data)
    )

    await db.commit()
    await db.refresh(db_project)
    return db_project


@router.delete("/{project_id}", response_model=ProjectSchema, status_code=status.HTTP_200_OK)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await db.scalars(stmt)
    db_project = result.first()

    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Project not found')

    await db.execute(
        update(ProjectModel).
        where(ProjectModel.id == project_id).
        values(is_active=False))
    await db.commit()
    await db.refresh(db_project)
    return db_project


@router.delete("/")
async def delete_all_projects(db: AsyncSession = Depends(get_async_db)) -> dict:
    stmt = select(ProjectModel).where(ProjectModel.is_active == True)
    result = await db.scalars(stmt)
    db_projects = result.all()

    for project in db_projects:
        await db.execute(
            update(ProjectModel).where(ProjectModel.id == project.id).values(is_active=False))

    await db.commit()

    return {"status": "success", "message": "Projects were deleted"}
