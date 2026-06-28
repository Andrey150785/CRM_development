from decimal import Decimal
from sqlalchemy import Integer, Numeric, Boolean, DateTime, Enum, ForeignKey
from datetime import datetime
import enum

from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.database import Base


class DealStatus(enum.Enum):
    on_sale = "on_sale"
    reservation = "reserved"
    confirmed = "confirmed"
    signing = "signing"
    payment = "payment"
    completed = "completed"
    canceled = "canceled"


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    deal_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(Enum(DealStatus), nullable=False, default=DealStatus.on_sale)
    deal_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    object_id: Mapped[int] = mapped_column(ForeignKey("objects.id"), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="deals")
    client: Mapped["Client"] = relationship("Client", back_populates="deals")
    object: Mapped["Object"] = relationship("Object", back_populates="deal")

    def __repr__(self):
        return (f"Deal(id={self.id}, client_name={self.client_id}, is_completed={self.is_completed}, "
                f"deal_date={self.deal_date}, status={self.status})")
