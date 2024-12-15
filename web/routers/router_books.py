from fastapi import APIRouter, HTTPException, Request, Depends, status, Body, Form
import requests
from typing import Annotated, List
from fastapi.encoders import jsonable_encoder
from typing import Annotated, Optional
from ..core.books import read_all_books, read_user_books, add_book, search_book
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
    url = f"https://api.nytimes.com/svc/books/v3//lists/overview.json?api-key=eQJ6Y7m44qlYmsdykINA3ivVW3r48Ioy"
    response = requests.get(url).json()
    results = response["results"]
    published_date = results["published_date"]
    books_api = [
        # list for list in results["lists"] if list["display_name"] == "Mass Market"
        list for list in results["lists"]
    ][0]["books"]
    books_db = await read_all_books()
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "books_api": books_api,
            "books_db": books_db,
            "published_date": published_date,
            "msg": msg,
        },
    )


@router.get(
    "/books/", response_description="List all books", response_model=List[BaseBook]
)
async def read_items():
    books = await read_all_books()
    if not books:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No records found")
        raise RedirectException(status_code=404, 
                            detail="INF_No records found.",
                            loc = "/books")
    return books


# @router.get("/users/me/books/", response_description="List books of logged user", response_model=List[BookSchema])
# async def read_own_books(
#     current_user: Annotated[User, Depends(get_current_user)]
# ):
#     current_user = jsonable_encoder(current_user)
#     user_books = await read_user_books(current_user["email"])
#     if not user_books:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='not found')
#     return user_books


@router.get("/users/me/books/", response_description="List books of logged user")
async def read_own_books(request: Request, token=Depends(acccess_token_bearer)):
    errors = []
    # try:
        # if token is None:
        #     errors.append("Please log in to see library")
        #     return templates.TemplateResponse(
        #         request=request, name="login.html", context={"errors": errors}
        #     )
        # else:
            # scheme, _, param = token.partition(" ")
    # payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    payload = decode_token(token)
    email = payload.get("sub")
    user = await get_user(email)
    if user is None:
        errors.append("Email doesn't exist. Please create account.")
        return templates.TemplateResponse(
            request=request, name="register.html", context={"errors": errors}
        )
    else:
        user_books = await read_user_books(email)
        return templates.TemplateResponse(
            request=request,
            name="userlibrary.html",
            context={"user_books": user_books},
        )
    # except Exception as e:
    #     print(f'Error!!!{e}')


# @router.post("/users/me/addbook", response_description="Book data added into the db")
# async def add_new_book(
#     current_user: Annotated[User, Depends(get_current_user)], book: BaseBook = Body(...)
# ):
#     new_book = jsonable_encoder(book)
#     new_book["username"] = current_user.username
#     new_book = BookSchema(**new_book)
#     new_book = await add_book(new_book.model_dump())
#     return new_book


@router.post("/searchbook")
async def searchbook(
    request: Request,
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
):
    search_result = await search_book(title, author)
    return templates.TemplateResponse(
        request=request,
        name="searchbook.html",
        context={"search_result": search_result},
    )
