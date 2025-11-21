import uuid
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, init_db
from models import ItemModel


app = FastAPI(title="Items API")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True




@app.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)) -> List[Item]:
    """Get all items from database"""
    result = await db.execute(select(ItemModel))
    items = result.scalars().all()
    return [Item(name=item.name, description=item.description, price=item.price, in_stock=item.in_stock) for item in items]


@app.get("/items/{item_id}")
async def get_item(item_id: str, db: AsyncSession = Depends(get_db)) -> Item:
    """Get a specific item by UUID"""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await db.execute(select(ItemModel).where(ItemModel.id == item_uuid))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return Item(name=item.name, description=item.description, price=item.price, in_stock=item.in_stock)


@app.post("/items", status_code=201)
async def create_item(item: Item, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Create a new item in database"""
    db_item = ItemModel(
        name=item.name,
        description=item.description,
        price=item.price,
        in_stock=item.in_stock
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    
    return {"item_id": str(db_item.id), "item": item}


@app.put("/items/{item_id}")
async def update_item(item_id: str, item: Item, db: AsyncSession = Depends(get_db)) -> Dict[str, Item]:
    """Update an existing item in database"""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await db.execute(select(ItemModel).where(ItemModel.id == item_uuid))
    db_item = result.scalar_one_or_none()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.name = item.name
    db_item.description = item.description
    db_item.price = item.price
    db_item.in_stock = item.in_stock
    
    await db.commit()
    await db.refresh(db_item)
    
    return {"item": item}


@app.delete("/items/{item_id}")
async def delete_item(item_id: str, db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    """Delete an item from database"""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await db.execute(select(ItemModel).where(ItemModel.id == item_uuid))
    db_item = result.scalar_one_or_none()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await db.delete(db_item)
    await db.commit()
    
    return {"detail": "Item deleted"}
