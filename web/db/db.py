from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()


URI_DOCKER = "mongodb://mongodb:27017"

client = AsyncIOMotorClient(URI_DOCKER)

database = client.booksdb

books_collection = database.get_collection("books")
users_collection = database.get_collection("users")
blocklist_collection = database.get_collection("blocklist")


# db_manager = DBManager(uri=os.getenv("URI_MONGODBATLAS"), database_name="fastapidb")

# db_manager = DBManager(uri=os.getenv("URI_DOCKER"), database_name="db_local")

# db_manager = DBManager(uri="mongodb://mongodb:27017", database_name="booksdb")
