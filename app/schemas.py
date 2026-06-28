from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, EmailStr


class Project(BaseModel):
    id: int = Field(..., description='id of actual project')
    name: str = Field(..., description='name of actual projects')
    finish_time: datetime = Field(..., description='finish time of actual project')
    is_active: bool = Field(True, description='is actual project active')
    parent_id: int | None = Field(None, description='id of parent project')

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description='name of actual projects')
    finish_time: datetime = Field(..., description='finish time of actual project')
    is_active: bool = Field(True, description='is actual project active')
    parent_id: int | None = Field(None, description='id of parent project')


class Client(BaseModel):
    id: int = Field(..., description='id of actual client')
    name: str = Field(..., description='name of actual client')
    phone_number: str = Field(..., description='phone number of actual client')
    is_active: bool = Field(True, description='is actual client active')


class ClientCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description='name of actual client')
    phone_number: str = Field(..., description='phone number of actual client')
    is_active: bool = Field(True, description='is actual client active')

    model_config = ConfigDict(from_attributes=True)


class Object(BaseModel):
    id: int = Field(..., description='id of actual object')
    number: str = Field(..., description='number of actual object')
    floor: int = Field(..., description='floor of actual object')
    square: float = Field(..., description='square of actual object')
    price: float = Field(..., description='price of actual object')
    image_url: str | None = Field(None, description='image url of actual object')
    on_sale: bool = Field(True, description='is actual object on sale')
    project_id: int = Field(..., description='id of actual project')


class ObjectCreate(BaseModel):
    number: str = Field(..., description='number of actual object')
    floor: int = Field(..., description='floor of actual object')
    square: float = Field(..., description='square of actual object')
    price: float = Field(..., description='price of actual object')
    image_url: str | None = Field(None, description='image url of actual object')
    on_sale: bool = Field(True, description='is actual object on sale')
    project_id: int = Field(..., description='id of actual project')

    model_config = ConfigDict(from_attributes=True)


class ObjectList(BaseModel):
    """
    Список пагинации сделок пользователя
    """
    objects: list[Object] = Field(description='Список квартир')
    total: int = Field(ge=0, description='Общее количество квартир')
    page: int = Field(ge=1, description='Номер страницы')
    page_size: int = Field(ge=1, description='Количество элементов на странице')

    model_config = ConfigDict(from_attributes=True)


class Deal(BaseModel):
    id: int = Field(..., description='id of actual deal')
    is_completed: bool = Field(False, description='is actual deal completed')
    deal_date: datetime = Field(..., description='date of actual deal')
    status: str = Field(..., description='status of actual deal')
    deal_price: float = Field(..., description='price of actual deal')
    client_id: int = Field(..., description='id of actual client')
    object_id: int = Field(..., description='id of actual object')
    user_id: int = Field(..., description='id of actual user')

    model_config = ConfigDict(from_attributes=True)


class DealCreate(BaseModel):
    is_completed: bool = Field(False, description='is actual deal completed')
    status: str = Field(..., description='status of actual deal')
    deal_price: float = Field(..., description='price of actual deal')
    client_id: int = Field(..., description='id of actual client')
    object_id: int = Field(..., description='id of actual object')
    # user_id: int = Field(..., description='id of actual user')

    model_config = ConfigDict(from_attributes=True)


class DealList(BaseModel):
    """
    Список пагинации сделок пользователя
    """
    deals: list[Deal] = Field(description='Список сделок')
    total: int = Field(ge=0, description='Общее количество сделок')
    page: int = Field(ge=1, description='Номер страницы')
    page_size: int = Field(ge=1, description='Количество элементов на странице')

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr = Field(description="Email пользователя")
    hashed_password: str = Field(min_length=8, description="Пароль (минимум 8 символов)")
    role: str = Field(default="reader", pattern="^(reader|admin)$", description="Роль: 'reader' or 'admin'")


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str
