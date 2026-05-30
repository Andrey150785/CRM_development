from datetime import datetime

from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    finish_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    objects: Mapped[list["Object"]] = relationship("Object", back_populates="project")
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)

    parent: Mapped["Project | None"] = relationship("Project", back_populates="children", remote_side="Project.id")
    children: Mapped[list["Project"]] = relationship("Project", back_populates="parent")

    def __repr__(self):
        return f"Project(id={self.id}, name={self.name}, is_active={self.is_active})"