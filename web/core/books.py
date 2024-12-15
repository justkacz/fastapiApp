from ..db.db import books_collection
import requests
from fastapi import HTTPException, status


async def read_all_books() -> list:
    books = []
    async for book in books_collection.find():
        # book['id'] = str(book['_id'])
        # del[book['_id']]
        books.append(book)
    return books


async def read_user_books(username: str) -> list:
    user_books = []
    async for book in books_collection.find({"username": username}):
        # book['id'] = str(book['_id'])
        # del[book['_id']]
        user_books.append(book)
    return user_books


async def add_book(book_data: dict) -> dict:
    book = await books_collection.insert_one(book_data)
    new_book = await books_collection.find_one(
        {"_id": book.inserted_id}, {"_id": False}
    )
    return new_book


async def search_book(title: str, author: str):
    API_KEY = "AIzaSyAbFstk55PIArsCEJA4y2BomWhS3Cb_Fzo"
    url = f"https://www.googleapis.com/books/v1/volumes?q={title}+inauthor:{author}&key={API_KEY}"
    response = requests.get(url).json()
    if "items" in response:
        all_results = []
        for i in range(len(response["items"])):
            all_results.append(
                {
                    "title": response["items"][i]["volumeInfo"]["title"],
                    "authors": response["items"][i]["volumeInfo"].get(
                        "authors", "Data not available"
                    )[0],
                    "publishedDate": response["items"][i]["volumeInfo"].get(
                        "publishedDate", "Data not available"
                    ),
                    "language": response["items"][i]["volumeInfo"].get(
                        "language", "Data not available"
                    ),
                    # "image": response['items'][i]['volumeInfo'].get("imageLinks", "Image not available").get("thumbnail", "Image not available"),
                    "infoLink": response["items"][i]["volumeInfo"].get(
                        "infoLink", "Data not available"
                    ),
                }
            )
        return all_results
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No records found")
