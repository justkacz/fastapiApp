from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


class DBManager:
    def __init__(self, uri: str, database_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[database_name]

    async def create_item(self, item):
        result = await self.db.items.insert_one(item)
        return await self.read_item(result.inserted_id)

    async def read_item(self, item_id: ObjectId):
        item = await self.db.items.find_one({"_id": item_id})
        if item:
            item["id"] = str(item["_id"])
            del item["_id"]
        return item

    async def read_items(self) -> list:
        items = []
        cursor = self.db.items.find({})
        async for item in cursor:
            item["id"] = str(item["_id"])
            del item["_id"]
            items.append(item)
        return items

    async def update_item(self, item_id: ObjectId, item):
        await self.db.items.update_one({"_id": item_id}, {"$set": item})
        return await self.read_item(item_id)

    async def delete_item(self, item_id: ObjectId) -> bool:
        result = await self.db.items.delete_one({"_id": item_id})
        return result.deleted_count > 0


db_manager = DBManager(uri="mongodb://mongodb:27017", database_name="db_local")
