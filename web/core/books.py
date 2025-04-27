from ..db.db import books_collection
import requests
import re
from fastapi import HTTPException, status
from datetime import datetime
import math

API_KEY = "AIzaSyAbFstk55PIArsCEJA4y2BomWhS3Cb_Fzo"

def api_volume_details(volumeid: str) -> dict:
    book_data={}
    # print(volumeid)
    url = f"https://www.googleapis.com/books/v1/volumes/{volumeid}?key={API_KEY}"
    response = requests.get(url).json()
    book_data['id']=response.get('id', None)
    book_data['category']=response['volumeInfo'].get('categories', ["General"])[0].split('/')[0]
    if 'authors' not in response['volumeInfo']:
        book_data['authors']='Author Unknown'
    elif len(response['volumeInfo']['authors']) > 1:
        book_data['authors']=(', ').join(response['volumeInfo']['authors'][:3])
    else:
        book_data['authors']=response['volumeInfo']['authors'][0]
    book_data['title']=response['volumeInfo'].get('title', None)
    book_data['description']=re.sub(r'<.[a-z]>|<[a-z]>', '', response['volumeInfo'].get('description', 'Description not available.'))
    # book_data['description']=response['volumeInfo'].get('description', None)
    book_data['rating'] = response['volumeInfo'].get('averageRating', 0)
    book_data['ratingcnt'] = response['volumeInfo'].get('ratingsCount', 0)
    book_data['publishedDate']=response['volumeInfo'].get('publishedDate', None)
    # book_data['imageLinks']=response['volumeInfo']['imageLinks'].get('medium', None)
    book_data['imageLinks']=response['volumeInfo'].get('imageLinks', None)
    book_data['previewLink']=response['volumeInfo'].get('previewLink', 'http://books.google.pl')
    return book_data





async def recently_added() -> list:
    books = []
    async for book in books_collection.find().sort({ '_id' : -1 }).limit(4):
        book_data=api_volume_details(book['volumeid'])
        book_data['datediff'] = (datetime.now().date() - book['createdon'].date()).days
        books.append(book_data)
    return books



async def read_user_books(username: str) -> list:
    books_db = [doc async for doc in books_collection.find({"username": username})]
    if books_db is not None:
        user_books = []
        for book in books_db:
            book_data=api_volume_details(book['volumeid'])
            user_books.append(book_data)
    return user_books


async def add_book(book_data: dict) -> dict:
    book_exist = await books_collection.find_one(
        {"volumeid": book_data['volumeid'], "username": book_data['username']}
    )
    print('*************************************************************book_exist', book_exist)
    if book_exist is None:
        book = await books_collection.insert_one(book_data)
        new_book = await books_collection.find_one(
            {"_id": book.inserted_id}, {"_id": False}
        )
        print('*************************************************************new_book', new_book)
        return new_book
    return None

async def delete_book(volumeid: str, email: str):
    await books_collection.delete_one({"volumeid": volumeid, "username": email})


async def search_book(title: str, author: str, subject: str):
    url = f"https://www.googleapis.com/books/v1/volumes?q={title}+inauthor:{author}+intitle:{title}+insubject:{subject}&printType=books&maxResults=40&key={API_KEY}"
    print(url)
    response_search = requests.get(url).json()
    # print("title:",title)
    # print("author:",author)
    # print("subject:",subject)
    # print("response:",response_search)
    if "items" in response_search:
        pages = []
        ranges = []
        n=12
        for j in range(0,math.ceil(len(response_search['items'])/12)):
            pages.append(j+1)
            ranges.append(slice(j*n, j*n+n))
        all_results = []
        for i in range(len(response_search["items"])):
            # v_url = f"https://www.googleapis.com/books/v1/volumes/{response["items"][i]["id"]}?key={API_KEY}"
            # v_response = requests.get(v_url).json()
            # print('volumeid:', response_search["items"][i]["id"])
            volume_details = api_volume_details(response_search["items"][i]["id"])
            # print('volume_details:', volume_details)
            all_results.append(
                {
                    "volumeid": response_search["items"][i]["id"],
                    "title": response_search["items"][i]["volumeInfo"].get("title", None),
                    "authors": response_search["items"][i]["volumeInfo"].get(
                        "authors", "Data not available"
                    )[0],
                    "publishedDate": response_search["items"][i]["volumeInfo"].get(
                        "publishedDate", "Data not available"
                    ),
                    # "description": volume_details['description'],
                    # "rating": volume_details['rating'],
                    # "ratingcnt": volume_details['ratingcnt'],
                    # "category": volume_details['category'],
                    "volume_details": volume_details,
                    "language": response_search["items"][i]["volumeInfo"].get(
                        "language", "Data not available"
                    ),
                    # "image": response['items'][i]['volumeInfo'].get("imageLinks", "Image not available").get("thumbnail", "Image not available"),
                    "infoLink": response_search["items"][i]["volumeInfo"].get(
                        "infoLink", "Data not available"
                    ),
                }
            )
            # print('*******************************************************************************************************all_results',i, all_results[i])
        return all_results, pages, ranges
    else:
        return None
