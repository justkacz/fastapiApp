from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()


# URI_DOCKER = "mongodb://mongodb:27017"
URI_MONGODBATLAS = "mongodb+srv://fastapi:fastapi@cluster0.qyn7o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# client = AsyncIOMotorClient(URI_DOCKER)
client = AsyncIOMotorClient(URI_MONGODBATLAS)

database = client.booksdb

books_collection = database.get_collection("books")
users_collection = database.get_collection("users")
blocklist_collection = database.get_collection("blocklist")


# db_manager = DBManager(uri=os.getenv("URI_MONGODBATLAS"), database_name="fastapidb")

# db_manager = DBManager(uri=os.getenv("URI_DOCKER"), database_name="db_local")

# db_manager = DBManager(uri="mongodb://mongodb:27017", database_name="booksdb")
