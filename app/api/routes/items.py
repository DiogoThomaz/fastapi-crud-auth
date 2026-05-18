from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select

from app.core.deps import get_current_user
from app.db.session import SessionLocal
from app.models.item import Item
from app.models.user import User
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, _: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        item = Item(name=payload.name, description=payload.description)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()


@router.get("/{id}", response_model=ItemResponse)
def get_item(id: int, _: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        item = db.execute(select(Item).where(Item.id == id)).scalars().first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        return item
    finally:
        db.close()


@router.get("", response_model=list[ItemResponse])
def list_items(
    _: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    db = SessionLocal()
    try:
        stmt = select(Item).order_by(Item.id.desc()).offset((page - 1) * page_size).limit(page_size)
        items = db.execute(stmt).scalars().all()
        return items
    finally:
        db.close()


@router.put("/{id}", response_model=ItemResponse)
def update_item(id: int, payload: ItemUpdate, _: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        item = db.execute(select(Item).where(Item.id == id)).scalars().first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

        data = payload.model_dump(exclude_unset=True)
        if "name" in data and data["name"] is not None:
            item.name = data["name"]
        if "description" in data:
            item.description = data["description"]

        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(id: int, _: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        item = db.execute(select(Item).where(Item.id == id)).scalars().first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        db.delete(item)
        db.commit()
        return None
    finally:
        db.close()