from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="Items API")


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True


# In-memory storage for items
items_db: Dict[int, Item] = {}


@app.get("/items")
async def list_items() -> Dict[int, Item]:
    return items_db


@app.get("/items/{item_id}")
async def get_item(item_id: int) -> Item:
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@app.post("/items", status_code=201)
async def create_item(item_id: int, item: Item) -> Dict[str, Item]:
    if item_id in items_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    items_db[item_id] = item
    return {"item": item}


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item) -> Dict[str, Item]:
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_id] = item
    return {"item": item}


@app.delete("/items/{item_id}")
async def delete_item(item_id: int) -> Dict[str, str]:
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return {"detail": "Item deleted"}
