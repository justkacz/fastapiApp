from fastapi import FastAPI, Request, responses
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from .core.error_handler import RedirectException
from dotenv import load_dotenv
from pydantic import ValidationError


load_dotenv()

templates = Jinja2Templates(directory="web/templates")

from web.routers import router_books, router_users


# async def http_exception(request: Request, exc: HTTPException):
#     message = exc.detail
#     return templates.TemplateResponse(
#         request=request,
#         name=f"{exc.headers['Location']}.html",
#         context={"msg": message},
#         status_code=exc.status_code,
#     )

# async def responseredirect(request: Request, exc: HTTPException):
#     message = exc.detail
#     return responses.RedirectResponse(
#         f"{exc.headers['Location']}?msg={message}",
#         status_code=302,
#     )


# exception_handlers = { 302: responseredirect, 404: http_exception, 403: http_exception,
#                       401: http_exception}

# app = FastAPI(exception_handlers=exception_handlers)
app = FastAPI()
app.mount("/static", StaticFiles(directory="web/static"), name="static")

app.include_router(router_users.router, tags=["users"])
app.include_router(router_books.router, tags=["books"])


@app.exception_handler(RedirectException)
async def unicorn_exception_handler(request: Request, exc: RedirectException):
    return responses.RedirectResponse(
        f"{exc.loc}?msg={exc.detail}",
        status_code=302,
    )

# @app.exception_handler(ValidationError)
# async def handler_validation_error(request, exc):
#     return responses.RedirectResponse(
#         f"login?msg=Password should be minimum 4 letters",
#         status_code=302,
#     )