import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from bson import ObjectId


BaseModel.model_config["json_encoders"] = {ObjectId: lambda v: str(v)}


class User(BaseModel):
    # username: str = Field(...)
    email: EmailStr = Field(...)  # required
    full_name: Optional[str] = None


class UserInDB(User):
    hashed_password: str


class RegisterUser(User):
    password: str = Field(...)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class BaseBook(BaseModel):
    # id: str = Field(default_factory=uuid.uuid4, alias='_id')
    title: str = Field(...)
    author: str = Field(...)
    description: Optional[str] = None
    # createdon: datetime = datetime.now()

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                # "_id": "06gh679-f34b-8b26-147g-665f26g0765ij45k",
                "title": "Sample Title",
                "author": "Sample Author",
                "description": "Sample Description",
            }
        }


class BookSchema(BaseBook):
    # id: str = Field(default_factory=uuid.uuid4, alias='_id')
    username: str = Field(...)
    createdon: datetime = datetime.now()


class BookUpdate(BaseModel):
    title: str = Optional[str]
    author: str = Optional[str]
    description: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "Sample Title",
                "author": "Sample Author",
                "description": "Updated Description...",
            }
        }
