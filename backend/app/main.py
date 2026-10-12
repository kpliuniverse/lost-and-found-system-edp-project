from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Item
from .schemas import ItemCreate, ItemOut, Status
from .security import hash_pin, verify_pin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lost and Found API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_item_or_404(item_id: int, db: Session) -> Item:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "This post does not exist (it may have been deleted).")
    return item


def require_pin(item: Item, pin: str) -> None:
    if not pin or not verify_pin(pin, item.pin_hash):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Wrong PIN. Please check it and try again.")


# ---------- LIST + SEARCH ----------
@app.get("/api/items", response_model=list[ItemOut])
def list_items(
    q: str | None = None,
    status: Status | None = None,
    category: str | None = None,
    include_resolved: bool = False,
    db: Session = Depends(get_db),
):
    stmt = select(Item)

    if status:
        stmt = stmt.where(Item.status == status)
    if category:
        stmt = stmt.where(Item.category == category)
    if not include_resolved:
        stmt = stmt.where(Item.is_resolved.is_(False))

    # Every word typed must match the title, description, location or category.
    for word in (q or "").split():
        like = f"%{word}%"
        stmt = stmt.where(
            or_(
                Item.title.ilike(like),
                Item.description.ilike(like),
                Item.location.ilike(like),
                Item.category.ilike(like),
            )
        )

    stmt = stmt.order_by(Item.created_at.desc())
    return db.scalars(stmt).all()


# ---------- VIEW ONE ----------
@app.get("/api/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    return get_item_or_404(item_id, db)


# ---------- ADD / CREATE ----------
@app.post("/api/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude={"pin"})
    item = Item(**data, pin_hash=hash_pin(payload.pin))
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# ---------- MARK AS RETURNED ----------
@app.patch("/api/items/{item_id}/resolve", response_model=ItemOut)
def mark_returned(
    item_id: int,
    pin: str = Header(default="", alias="X-Item-PIN"),
    db: Session = Depends(get_db),
):
    item = get_item_or_404(item_id, db)
    require_pin(item, pin)
    item.is_resolved = True
    db.commit()
    db.refresh(item)
    return item


# ---------- DELETE ----------
@app.delete("/api/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    pin: str = Header(default="", alias="X-Item-PIN"),
    db: Session = Depends(get_db),
):
    item = get_item_or_404(item_id, db)
    require_pin(item, pin)
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
