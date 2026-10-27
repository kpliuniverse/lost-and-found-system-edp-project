from copy import deepcopy
from functools import lru_cache
import logging

import ollama
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.DEBUG)

from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import Depends, FastAPI, Header, HTTPException, Response, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from sqlalchemy import or_, select, func
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Item, PostImage
from .schemas import ItemCreate, ItemOut, Status
from .security import hash_pin, verify_pin
from PIL import Image

TEXT_SIMILARITY_THRESHOLD = 0.65
TEXT_SIMILARITY_WEIGHT = 0.35
IMAGE_SIMILARITY_THRESHOLD = 0.50
IMAGE_SIMILARITY_WEIGHT = 0.65
FINAL_SIMILARITY_THRESHOLD = 1
SCORE_IF_NO_IMAGE = 0.75
SCORE_IF_NO_DESC = 0.4

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lost and Found API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
MODEL_NAME = "sentence-transformers/clip-ViT-B-32"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    # Load once, not once per API request.
    return SentenceTransformer(MODEL_NAME)

def embed_text_for_image(text: str) -> list[float]:
    model = get_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def embed_image(image: Image.Image) -> list[float]:
    model = get_model()

    image = image.convert("RGB")

    embedding = model.encode(
        image,
        normalize_embeddings=True,
    )

    return embedding.tolist()

def gen_embedding_string(item: ItemCreate | Item):
    return (
        f"{item.title},"
        f"{item.description}, "
        f"Found in {item.location}"
    )

def gen_img_embedding_string(item: ItemCreate | Item):
    return f"{item.title}, {item.description}"

def get_embedding(text: str) -> list[float]:
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
            with Image.open(UPLOAD_DIR / image_path) as image:
                embedding = embed_image(image)
            item.images.append(PostImage(filename=image_path, post=item, image_embedding=embedding))
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

    
    text_embedding_statement = Item.embedding.cosine_distance(get_embedding(gen_embedding_string(item)))
    image_embedding_statement = PostImage.image_embedding.cosine_distance(embed_text_for_image(gen_img_embedding_string(item)))

    text_sim = (
                    select(Item.id.label("id"), text_embedding_statement.label("text_dist"))
                #   .order_by(text_embedding_statement)
                    .filter(Item.status != item.status)
                    .filter(text_embedding_statement < TEXT_SIMILARITY_THRESHOLD)
                    .cte("text_similarities")
                )

    image_sim = (
                    select(Item.id.label("id"), image_embedding_statement.label("image_dist"))
                    .join(PostImage, PostImage.post_id == Item.id)
                    .distinct(Item.id)
                    .filter(Item.status != item.status)
                    .filter(image_embedding_statement < IMAGE_SIMILARITY_THRESHOLD)
                    .order_by(Item.id, image_embedding_statement)
                    .cte("image_similarities")
                )

    final_dist_exp = (func.coalesce(text_sim.c.text_dist, SCORE_IF_NO_DESC) * TEXT_SIMILARITY_WEIGHT + func.coalesce(image_sim.c.image_dist, SCORE_IF_NO_IMAGE) * IMAGE_SIMILARITY_WEIGHT)
    final_dists = (select(text_sim.c.id.label("id"), final_dist_exp.label("final_dist"))
            .join(image_sim, text_sim.c.id == image_sim.c.id, isouter=True, full=True)
            .filter(final_dist_exp < FINAL_SIMILARITY_THRESHOLD)
            ).cte("final_dists")
    
    
    
    
    return (db.scalars(select(Item)
        .join(final_dists, Item.id == final_dists.c.id)
        .order_by(final_dists.c.final_dist)
    ).all())