from copy import deepcopy
import logging

import ollama

logging.basicConfig(level=logging.DEBUG)

from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import Depends, FastAPI, Header, HTTPException, Response, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Item, PostImage
from .schemas import ItemCreate, ItemOut, Status
from .security import hash_pin, verify_pin

SIMILARITY_THRESHOLD = 0.45

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lost and Found API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def gen_embedding_string(item: ItemCreate | Item):
    return (
        f"{item.title},"
        f"{item.description}, "
        f"Found in {item.location}"
    )

def get_embedding(text: str):
    response = ollama.embed(model="nomic-embed-text", input=text)
    logging.debug("Embeddings = %i", len(response.embeddings))
    return response["embeddings"][0]

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

UPLOAD_DIR = Path("/image_uploads")

UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/uploadimage")
def upload_image(file: UploadFile):
    if file.filename is None or file.filename == "":
        raise HTTPException(status_code=400, detail="No file selected")

    while (dst := UPLOAD_DIR / f"{str(uuid4())}{Path(file.filename).suffix}").exists():
        pass

    with open(dst, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "location": f"/static/image/{dst.name}"
    }

@app.get("/static/image/{filename}", response_class=FileResponse)
def get_image(filename: str):
    path = UPLOAD_DIR / filename
    logging.info("Getting %s", path.as_posix())
    if path.exists():
        return path
    else:
        logging.info("%s doesn't seem to exist", path.as_posix())
        raise HTTPException(status_code=404)

# ---------- ADD / CREATE ----------
@app.post("/api/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude={"pin", "image_filenames"})
    embedding_str = gen_embedding_string(payload)
    
    item = Item(**data, embedding=get_embedding(embedding_str), pin_hash=hash_pin(payload.pin))
    db.add(item)
    db.commit()
    db.refresh(item)
    
    if payload.image_filenames:
        non_existent_images = []
        for image_path in payload.image_filenames:
            if not (image_path := UPLOAD_DIR / image_path).exists():
                non_existent_images.append(f"'{image_path.as_posix()}'")
        if non_existent_images:
            raise HTTPException(status_code=400, detail=f"Images {', '.join(non_existent_images)} do not exist")
        for image_path in payload.image_filenames:
            item.images.append(PostImage(filename=image_path, post=item))
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


@app.get("/api/similaritems/{item_id}", response_model=list[ItemOut])
def get_similar_items(item_id: int, db: Session = Depends(get_db)):
    
    item = get_item_or_404(item_id, db)
    embedding_statement = Item.embedding.cosine_distance(get_embedding(gen_embedding_string(item)))
    return db.scalars(select(Item)
                      .order_by(embedding_statement)
                      .filter(Item.status != item.status)
                      .filter(embedding_statement < SIMILARITY_THRESHOLD)).all()
