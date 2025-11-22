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


class ItemCreate(BaseModel):
    """Schema for creating/updating items (optional id)"""
    id: Optional[str] = None  # Optional: if not provided, server generates UUID
    name: str
    description: Optional[str] = None
    price: float
    in_stock: Optional[bool] = True


class ItemResponse(BaseModel):
    """Schema for item responses (includes id)"""
    id: str
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool

    class Config:
        from_attributes = True


@app.get("/health")
async def healthcheck(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Health check endpoint - verifies API and database connectivity"""
    try:
        # Test database connection by executing a simple query
        await db.execute(select(1))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "api": "healthy",
        "database": db_status
    }


@app.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)) -> List[ItemResponse]:
    """Get all items from database"""
    result = await db.execute(select(ItemModel))
    items = result.scalars().all()
    return [
        ItemResponse(
            id=str(item.id),
            name=item.name,
            description=item.description,
            price=item.price,
            in_stock=item.in_stock
        )
        for item in items
    ]


@app.get("/items/{item_id}")
async def get_item(item_id: str, db: AsyncSession = Depends(get_db)) -> ItemResponse:
    """Get a specific item by UUID"""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await db.execute(select(ItemModel).where(ItemModel.id == item_uuid))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return ItemResponse(
        id=str(item.id),
        name=item.name,
        description=item.description,
        price=item.price,
        in_stock=item.in_stock
    )


@app.post("/items", status_code=201)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)) -> ItemResponse:
    """Create a new item in database with auto-generated UUID if not provided"""
    # Use provided ID or generate a random UUID
    if item.id:
        try:
            item_uuid = uuid.UUID(item.id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")
    else:
        item_uuid = uuid.uuid4()
    
    # Check if item with this ID already exists
    result = await db.execute(select(ItemModel).where(ItemModel.id == item_uuid))
    existing_item = result.scalar_one_or_none()
    if existing_item:
        raise HTTPException(status_code=400, detail="Item with this ID already exists")
    
    db_item = ItemModel(
        id=item_uuid,
        name=item.name,
        description=item.description,
        price=item.price,
        in_stock=item.in_stock if item.in_stock is not None else True
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    
    return ItemResponse(
        id=str(db_item.id),
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        in_stock=db_item.in_stock
    )


@app.put("/items/{item_id}")
async def update_item(item_id: str, item: ItemCreate, db: AsyncSession = Depends(get_db)) -> ItemResponse:
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
    db_item.in_stock = item.in_stock if item.in_stock is not None else db_item.in_stock
    
    await db.commit()
    await db.refresh(db_item)
    
    return ItemResponse(
        id=str(db_item.id),
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        in_stock=db_item.in_stock
    )


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
