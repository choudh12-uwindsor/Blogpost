import datetime
from typing import List, Optional
from uuid import UUID

from hashlib import md5
from pydantic import BaseModel, StrictStr, EmailStr, field_validator


class UserRecord(BaseModel):
    user_id: StrictStr
    first_name: StrictStr
    last_name: StrictStr
    username: StrictStr
    email: EmailStr
    password: StrictStr
    registered_date: datetime.datetime

    @field_validator('user_id', mode='before')
    @classmethod
    def validate_uuid(cls, v):
        UUID(v, version=4)
        return v

    @field_validator('password', mode='after')
    @classmethod
    def create_hash(cls, v: str):
        return md5(v.encode("utf8")).hexdigest()


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
    comment_id: StrictStr
    blog_id: StrictStr
    author_id: StrictStr
    content: StrictStr
    created_date: datetime.datetime
    updated_date: Optional[datetime.datetime] = None

    @field_validator('author_id', 'blog_id', mode='before')
    @classmethod
    def validate_uuid(cls, v):
        UUID(v, version=4)
        return v
