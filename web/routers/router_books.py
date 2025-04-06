from fastapi import APIRouter, HTTPException, Request, Depends, status, Body, Form, responses
import requests
from datetime import datetime
from typing import Annotated, List
from fastapi.responses import JSONResponse
from typing import Annotated, Optional, Any
from ..core.books import recently_added, read_user_books, add_book, search_book, delete_book
from ..core.error_handler import RedirectException
from ..core.security import (
    get_user,
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    decode_token,
    register_user,
    verify_password,
    acccess_token_bearer
)
from ..db.models import User, BaseBook, BookSchema
from web.main import templates
import jwt


router = APIRouter()


@router.get("/")
async def root(request: Request, msg: str = None):
    # return templates.TemplateResponse("base.html", {"request":request})
    # url=f'https://api.nytimes.com/svc/books/v3//lists/overview.json?api-key={os.getenv("NYT_KEY")}'
    # url = f"https://api.nytimes.com/svc/books/v3//lists/overview.json?api-key=eQJ6Y7m44qlYmsdykINA3ivVW3r48Ioy"
    url= f"https://api.nytimes.com/svc/books/v3/lists/current/mass-market-monthly.json?api-key=eQJ6Y7m44qlYmsdykINA3ivVW3r48Ioy"
    response = requests.get(url).json()
    results = response["results"]
    published_date = results["published_date"]
    bestsellers_date = results["bestsellers_date"]
    list_len = results["normal_list_ends_at"]
    # books_api = [
    #     list for list in results["lists"]
    # ][0]["books"]
    books_api = results["books"]
    books_db = await recently_added()
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "books_api": books_api,
            "books_db": books_db[:4],
            "published_date": published_date,
            "bestsellers_date": bestsellers_date,
            "list_len": list_len,
            "today": datetime.now(),
            "msg": msg,
        },
    )


@router.get("/users/me/books/", response_description="List books of logged user")
async def read_own_books(request: Request, token=Depends(acccess_token_bearer)):
    payload = decode_token(token)
    email = payload.get("sub")
    user_books = await read_user_books(email)

    if user_books is not None:
        return templates.TemplateResponse(
            request=request,
            name="userlibrary.html",
            context={"user_books": user_books},
        )
    else:
        return templates.TemplateResponse(
            request=request,
            name="userlibrary.html",
            context={"norecords": "Your Library is empty."},
        )


@router.post("/users/me/addbook/", response_description="Book data added into the db")
async def add_new_book(
    volumeid:str=Body(...), token=Depends(acccess_token_bearer)
) -> Any:
    payload = decode_token(token)
    email = payload.get("sub")
    new_book={}
    new_book['volumeid'] = volumeid
    new_book["username"] = email
    new_book["createdon"] = datetime.now()
    print(new_book)
    await add_book(new_book)
    data = {"msg": "Book has been added to your library"}
    return JSONResponse(content=data)

# @router.post("/users/me/addbook/{volumeid}", response_description="Book data added into the db")
# async def add_new_book(
#     volumeid:str, token=Depends(acccess_token_bearer)
# ) -> Any:
#     payload = decode_token(token)
#     email = payload.get("sub")
#     new_book={}
#     new_book['volumeid'] = volumeid
#     new_book["username"] = email
#     new_book["createdon"] = datetime.now()
#     await add_book(new_book)


@router.get("/users/me/deletebook/{volumeid}", response_description="Book data removed from the db")
async def deletebook(
    request: Request, volumeid:str, token=Depends(acccess_token_bearer)
) -> Any:
    payload = decode_token(token)
    email = payload.get("sub")
    print("volid", volumeid)
    await delete_book(volumeid, email)
    # user_books = await read_user_books(email)
    # if user_books is not None:
    return responses.RedirectResponse(
        "/users/me/books/",
        status_code=302,
    )


@router.post("/searchbook")
async def searchbook(
    request: Request,
    title: Optional[str] = Form(""),
    author: Optional[str] = Form(""),
    subject: Optional[str] = Form(""),
):
    try:
        search_result, pages, ranges = await search_book(title, author, subject)
        # if search_result is not None:
        return templates.TemplateResponse(
                request=request,
                name="searchbook.html",
                context={"search_result": search_result, "title": title, "author": author, "subject": subject, "pages": pages, "ranges": ranges},
            )
    except:
        return templates.TemplateResponse(
            request=request,
            name="searchbook.html",
            context={"norecords": "No records found.", "title": title, "author": author, "subject": subject},
        )

