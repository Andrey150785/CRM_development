from contextlib import asynccontextmanager
# Импортируем необходимые библиотеки
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Импортируем роутеры
from app.routers import project_router, object_router, user_router, deal_router


# from app.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Приложение запускается. Создаем базу данных...')
    # await create_db_and_tables()
    print("База данных инициализирована.")
    yield
    print("Приложение завершает работу.")


app = FastAPI(
    title="Агрегированные данные из Домопланер",
    lifespan=lifespan
)


app.include_router(project_router)
app.include_router(object_router)
app.include_router(user_router)
app.include_router(deal_router)


# Настраиваем CORS для взаимодействия с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {"message": "Это проект данных из Домопланера"}
