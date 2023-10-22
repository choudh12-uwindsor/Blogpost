import datetime
from typing import Union, List, Optional
from uuid import UUID

import bcrypt
from pydantic import BaseModel, StrictStr, EmailStr, field_validator

from config import HASH_SALT


class UserRecord(BaseModel):
    user_id: StrictStr
    username: StrictStr
    email: EmailStr
    password: StrictStr
    registered_date: datetime.datetime

    @field_validator('user_id', mode='before')
    @classmethod
    def validate_uuid(cls, v):
        UUID(v, version=4)
        return v

    @field_validator('password', mode='before')
    @classmethod
    def create_hash(cls, v):
        return bcrypt.hashpw(v.encode('utf-8'), HASH_SALT).decode('utf8')


class BlogRecord(BaseModel):
    blog_id: StrictStr
    title: StrictStr
    content: StrictStr
    author_id: StrictStr
    created_date: datetime.datetime
    updated_date: Optional[datetime.datetime] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None

    @field_validator('author_id', 'blog_id', mode='before')
    @classmethod
    def validate_uuid(cls, v):
        UUID(v, version=4)
        return v


class CommentRecord(BaseModel):
    blog_id: StrictStr
    author_id: StrictStr
    content: StrictStr
    created_date: datetime.datetime

    @field_validator('author_id', 'blog_id', mode='before')
    @classmethod
    def validate_uuid(cls, v):
        UUID(v, version=4)
        return v
