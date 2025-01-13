from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Depends,
    status,
    Form,
    Response,
    responses
)
from typing import Annotated, Optional
from fastapi.encoders import jsonable_encoder
from ..core.security import (
    authenticate_user,
    get_user,
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    create_access_token,
    register_user,
    decode_token,
    add_jti_to_blocklist,
    token_in_blocklist,
    acccess_token_bearer
)
from ..core.error_handler import RedirectException
from pydantic import ValidationError
from datetime import timedelta
from ..db.models import User, UserInDB, RegisterUser, Token
from fastapi.templating import Jinja2Templates
from web.main import templates
import jwt

# templates = Jinja2Templates(directory="./web/templates")

router = APIRouter()


# @router.post("/token")
# async def login_for_access_token(
#     response: Response,
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
# ) -> Token:
#     user = await authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user["email"]}, expires_delta=access_token_expires
#     )
#     response.set_cookie(
#         key="access_token", value=f"Bearer {access_token}", httponly=True
#     )
#     return Token(access_token=access_token, token_type="bearer")


# @router.get("/users/me/", response_model=User)
# async def read_users_me(
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     return current_user


@router.get("/register")
def register(request: Request, msg: str = None):
    return templates.TemplateResponse(request=request, name="register.html", context={"msg": msg})


@router.post("/register")
async def register(request: Request, email: str = Form(...), password: str = Form(...)):
    email_exist = await get_user(email)
    if email_exist:
            # raise HTTPException(status_code=403, 
            #                     detail="INF_The user with this email already exists.",
            #                     headers = {"Location": "register"})
            raise RedirectException(status_code=403, 
                                    detail="INF_The user with this email already exists.",
                                    loc = "/register")
    # try:     
    user = RegisterUser(email=email, password=password)
    # except ValidationError as e:
    #     raise RedirectException(status_code=403, 
    #                                 detail="INF_Password must have at least 4 characters.",
    #                                 loc = "/register")
    user = jsonable_encoder(user)
    new_user = await register_user(user_data=user)
    new_user = UserInDB(email=new_user["email"], hashed_password=new_user["password"])
    return responses.RedirectResponse(
        "/login?msg=SUC_Your account has been created. Please log in.",
        status_code=302
    )


@router.get("/login")
def login(request: Request, msg: str = None):
    return templates.TemplateResponse(
        request=request, name="login.html", context={"msg": msg}
    )


@router.post("/login")
async def login(response: Response, request: Request, email: str = Form(...), password: str = Form(...)):
    user = await get_user(email)
    if user is None:
        raise RedirectException(status_code=401,
                                detail="ERR_Email does not exist. Please create an account.",
                                loc="login")
    else:
        if await authenticate_user(email, password):
            jwt_token = create_access_token(email, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
            response = responses.RedirectResponse(
                        "/?msg=SUC_Login successful",
                        status_code=302
                    )
            response.set_cookie(
                key="access_token", value=f"Bearer {jwt_token}", httponly=True
            )
            return response
        else:
            raise RedirectException(status_code=401, 
                                    detail="ERR_Invalid password, please try again.",
                                    loc = "login")
        

@router.get("/logout")
async def logout(request: Request, token=Depends(acccess_token_bearer)):
    # payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    payload = decode_token(token)
    jti = payload.get("jti")
    await add_jti_to_blocklist(jti)
    return responses.RedirectResponse(
        "/login?msg=INF_You are successfully logged out.",
        status_code=302,
    )

