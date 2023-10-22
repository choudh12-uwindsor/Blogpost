import datetime
from typing import Union, List, Optional
from uuid import UUID

from pydantic import BaseModel, StrictStr, EmailStr, field_validator


class AuthUser(BaseModel):
    email: EmailStr
    password: StrictStr


class RegisterUser(AuthUser):
    username: StrictStr


class BlogID(BaseModel):
    blog_id: StrictStr


class CreateBlog(BaseModel):
    title: StrictStr
    content: StrictStr
    author_id: StrictStr
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None


class UpdateBlog(BlogID):
    title: Optional[StrictStr] = None
    content: Optional[StrictStr] = None
    author_id: StrictStr
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None


class DeleteBlog(BlogID):
    user_id: StrictStr


class ListBlog(BaseModel):
    search_string: Optional[StrictStr] = None
    user_id: StrictStr
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None


class CreateComment(BaseModel):
    blog_id: StrictStr
    content: StrictStr
    author_id: StrictStr
