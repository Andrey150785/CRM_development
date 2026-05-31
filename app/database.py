from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://crm_admin:150785@localhost:5433/crm_db"


async_engine = create_async_engine(DATABASE_URL, echo=True)


async_session_maker = async_sessionmaker(async_engine, class_= AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
