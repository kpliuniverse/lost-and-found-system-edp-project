from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, UniqueConstraint, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import VECTOR

from .database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Item(Base):

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    status: Mapped[str] = mapped_column(String(10), index=True)  # "lost" or "found"
    title: Mapped[str] = mapped_column(String(120))
    embedding: Mapped[list[float]] = mapped_column(VECTOR(768))
    category: Mapped[str] = mapped_column(String(40), index=True)
    location: Mapped[str] = mapped_column(String(160))
    event_date: Mapped[date] = mapped_column(Date)  # day it was lost / found
    contact_name: Mapped[str] = mapped_column(String(80))
    contact_info: Mapped[str] = mapped_column(String(120))
    pin_hash: Mapped[str] = mapped_column(String(200)) # never sent to the browser
    description: Mapped[str] = mapped_column(Text, default="")
    images: Mapped[list["PostImage"]] = relationship("PostImage", back_populates="post", cascade="all, delete-orphan", default_factory=list)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default_factory=utc_now)
    
class PostImage(Base):

    __tablename__ = "postimages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    filename: Mapped[str] = mapped_column(String())
    post_id: Mapped[int] = mapped_column(ForeignKey(Item.id), init=False)
    post: Mapped[Item] = relationship(back_populates="images")
    image_embedding: Mapped[list[float] | None] = mapped_column(VECTOR(512), nullable=True)
    __table_args__ = (
        UniqueConstraint("filename", "post_id"),
    )
