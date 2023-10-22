from uuid import uuid4

import uvicorn
from fastapi import FastAPI
from pymongo import MongoClient

from api_models import *
from config import MONGO_CREDS
from database_models import *

app = FastAPI()
db = MongoClient(**MONGO_CREDS)["blogpost"]


@app.put("/user/register")
def register_user(data: RegisterUser):
    record = UserRecord(user_id=str(uuid4()), username=data.username, email=data.email, password=data.password,
                        registered_date=datetime.datetime.now())

    if db.users.count_documents({"email": data.email}) > 0:
        return {"status": "successful", "message": "User already exists", "code": 400}

    try:
        db.users.insert_one(record.model_dump(mode="json"))
    except Exception:
        return {"status": "error", "message": "Internal server error", "code": 500}
    return {"status": "successful", "message": "OK", "code": 201}


@app.get("/user/authenticate")
def authenticate_user(data: AuthUser):
    hash_ = bcrypt.hashpw(data.password.encode('utf-8'), HASH_SALT).decode('utf8')
    if db.users.count_documents({"email": data.email, "password": hash_}) == 1:
        return {"status": "successful", "message": "User authenticated", "code": 200}
    else:
        return {"status": "successful", "message": "Invalid credentials", "code": 401}


@app.get("/blog/list")
def list_blogs(data: ListBlog):
    if db.users.count_documents({"user_id": data.user_id}) == 0:
        return {"status": "successful", "message": "Author does not exist", "code": 401}

    conditions = {}
    if data.search_string:
        conditions["title"] = f"/{data.search_string}/"
    if data.tags:
        conditions["$or"] = []
        for tag in data.tags:
            conditions["$or"].append({"tags": {"$in": [tag]}})
    if data.categories:
        if not conditions.get("$or"):
            conditions["$or"] = []
        for category in data.tags:
            conditions["$or"].append({"categories": {"$in": [category]}})

    records = [record for record in list(db.blogs.find(conditions)) if record.pop("_id")]
    return {"status": "successful", "message": "OK", "result": records, "code": 200}


@app.put("/blog/create")
def create_blog(data: CreateBlog):
    if db.users.count_documents({"user_id": data.author_id}) == 0:
        return {"status": "successful", "message": "Author does not exist", "code": 401}

    if db.blogs.count_documents({"title": data.title}) > 0:
        return {"status": "successful", "message": "Blog title exists", "code": 401}

    record = BlogRecord(author_id=data.author_id, title=data.title, content=data.content,
                        blog_id=str(uuid4()), created_date=datetime.datetime.now(), tags=data.tags,
                        categories=data.categories)

    try:
        db.blogs.insert_one(record.model_dump(mode="json"))
    except Exception:
        return {"status": "error", "message": "Internal server error", "code": 500}
    return {"status": "successful", "message": "OK", "code": 201}


@app.get("/blog/fetch")
def fetch_blog(data: BlogID):
    if db.blogs.count_documents({"blog_id": data.blog_id}) == 0:
        return {"status": "successful", "message": "Blog does not exist", "code": 401}

    record = db.blogs.find_one({"blog_id": data.blog_id})
    comments = [i for i in db.comments.find({"blog_id": data.blog_id}) if i.pop("_id")]

    record.pop("_id")
    record["comments"] = comments
    return {"status": "successful", "message": "OK", "result": record, "code": 200}


@app.put("/blog/update")
def update_blog(data: UpdateBlog):
    if db.users.count_documents({"user_id": data.author_id}) == 0:
        return {"status": "successful", "message": "Author does not exist", "code": 401}

    if db.blogs.count_documents({"blog_id": data.blog_id}) == 0:
        return {"status": "successful", "message": "Blog does not exist", "code": 401}

    json_data = data.model_dump(mode="json")
    json_data.pop("blog_id")
    json_data.pop("author_id")
    json_data["updated_date"] = datetime.datetime.now()
    try:
        db.blogs.update_one({"blog_id": data.blog_id}, json_data)
    except Exception:
        return {"status": "error", "message": "Internal server error", "code": 500}
    return {"status": "successful", "message": "OK", "code": 204}


@app.delete("/blog/delete")
def delete_blog(data: DeleteBlog):
    if db.blogs.count_documents({"blog_id": data.blog_id, "author_id": data.user_id}) == 0:
        return {"status": "successful", "message": "User does not have priviledge to delete the blog", "code": 401}

    try:
        db.blogs.delete_one({"blog_id": data.blog_id})
    except Exception:
        return {"status": "error", "message": "Internal server error", "code": 500}

    return {"status": "successful", "message": "OK", "code": 204}


@app.put("/comment/create")
def create_comment(data: CreateComment):
    if db.blogs.count_documents({"blog_id": data.blog_id}) == 0:
        return {"status": "successful", "message": "Blog does not exist", "code": 401}

    if db.users.count_documents({"user_id": data.author_id}) == 0:
        return {"status": "successful", "message": "Author does not exist", "code": 401}

    record = CommentRecord(author_id=data.author_id, content=data.content,
                           blog_id=data.blog_id, created_date=datetime.datetime.now())

    try:
        db.comments.insert_one(record.model_dump(mode="json"))
    except Exception:
        return {"status": "error", "message": "Internal server error", "code": 500}
    return {"status": "successful", "message": "OK", "code": 201}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
