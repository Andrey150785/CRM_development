from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    deals: Mapped[list['Deal']] = relationship('Deal', back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Client(id={self.id}, name={self.name}, is_active={self.is_active})"