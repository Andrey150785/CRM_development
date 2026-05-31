from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, String, Boolean, Numeric, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Object(Base):
    __tablename__ = "objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    square: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    on_sale: Mapped[bool] = mapped_column(Boolean, default=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    project: Mapped["Project"] = relationship("Project", back_populates="objects")
    deal: Mapped["Deal"] = relationship("Deal", back_populates="object", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Object(id={self.id}, number={self.number}, price={self.price}, on_sale={self.on_sale}, project_id={self.project_id}, created_at={self.created_at})"
