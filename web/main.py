from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from uuid import UUID, uuid4
from .db.db import db_manager
from typing import List


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    on_offer: bool = False


app = FastAPI()
app.mount("/static", StaticFiles(directory="web/static"), name="static")

templates = Jinja2Templates(directory="web/templates")

@app.get("/")
async def index(request:Request):
    return templates.TemplateResponse("base.html", {"request":request})


@app.post("/items/", response_model=Item)
async def create_item(item: Item):   
    new_item = await db_manager.create_item(item.model_dump())
    return new_item


@app.get("/items/", response_model=List[Item])
async def read_items():
    return await db_manager.read_items()


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    item = await db_manager.read_item(ObjectId(item_id))
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    updated_item = await db_manager.update_item(ObjectId(item_id), item.model_dump())
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item


@app.delete("/items/{item_id}", response_model=str)
async def delete_item(item_id: str):
    deleted = await db_manager.delete_item(ObjectId(item_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return "Item deleted successfully"       
