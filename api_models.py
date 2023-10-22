import re
from typing import List, Optional

from pydantic import BaseModel, StrictStr, EmailStr, field_validator


class AuthUser(BaseModel):
    email: EmailStr
    password: StrictStr


class RegisterUser(AuthUser):
    username: StrictStr
    first_name: StrictStr
    last_name: StrictStr

    @field_validator('password', mode='before')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password length must be minimum 8 characters")
        elif not re.search(r"[a-z]", v) or not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain lower case and upper case characters")
        elif not re.search(r"[!@$&]", v) or not re.search(r"\d", v):
            raise ValueError("Password must contain special characters and digits")
        return v


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
