from uuid import uuid4

import pymongo
import uvicorn
from fastapi import FastAPI
from pymongo import MongoClient

from api_models import *
from config import MONGO_CREDS
from database_models import *

app = FastAPI()
db = MongoClient(**MONGO_CREDS)["blogpost"]
db.blogs.create_index([('title', 'text'), ('content', 'text')])


@app.put("/user/register")
def register_user(data: RegisterUser):
    record = UserRecord(user_id=str(uuid4()), username=data.username, email=data.email, password=data.password,
                        registered_date=datetime.datetime.now(), first_name=data.first_name,
                        last_name=data.last_name)

    if db.users.count_documents({"email": data.email}) > 0:
        return {"status": "successful", "message": "Email already exists", "code": 400}

    if db.users.count_documents({"username": data.username}) > 0:
        return {"status": "successful", "message": "Username already exists", "code": 400}

    try:
        db.users.insert_one(record.model_dump(mode="json"))
    except Exception:
        return {"status": "error", "message": "Internal server error", "code": 500}
    return {"status": "successful", "message": "OK", "code": 201}


@app.get("/user/authenticate")
def authenticate_user(data: AuthUser):
    hash_ = md5(data.password.encode("utf8")).hexdigest()
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
        conditions["$text"] = {"$search": f"/{data.search_string}/"}
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


@app.post("/blog/update")
def update_blog(data: UpdateBlog):
    if db.blogs.count_documents({"author_id": data.author_id, "blog_id": data.blog_id}) == 0:
        return {"status": "successful", "message": "User does not have priviledge to update the blog", "code": 401}

    json_data = data.model_dump(mode="json")
    json_data.pop("blog_id")
    json_data.pop("author_id")
    json_data["updated_date"] = datetime.datetime.now()
    json_data = {"$set": json_data}
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

    record = CommentRecord(author_id=data.author_id, content=data.content, comment_id=str(uuid4()),
                           blog_id=data.blog_id, created_date=datetime.datetime.now())

    try:
        db.comments.insert_one(record.model_dump(mode="json"))
    except Exception:
        return {"status": "error", "message": "Internal server error", "code": 500}
    return {"status": "successful", "message": "OK", "code": 201}


@app.get("/comment/list")
def list_comments(data: ListComment):
    if db.users.count_documents({"user_id": data.user_id}) == 0:
        return {"status": "successful", "message": "Unauthenticated user", "code": 401}

    try:
        result = []
        for record in db.comments.find({"blog_id": data.blog_id}):
            record.pop("_id")
            record.pop("blog_id")
            record["created_date"] = record["created_date"].strftime("%Y-%m-%d %H:%M")
            result.append(record)
        return {"status": "successful", "result": result, "code": 200}
    except Exception:
        return {"status": "error", "message": "Internal server error", "code": 500}


@app.delete("/comment/delete")
def delete_comment(data: DeleteComment):
    if db.comments.count_documents({"comment_id": data.comment_id, "author_id": data.user_id}) == 0:
        return {"status": "successful", "message": "User does not have priviledge to delete the comment", "code": 401}

    try:
        db.comments.delete_one({"comment_id": data.comment_id})
    except Exception:
        return {"status": "error", "message": "Internal server error", "code": 500}

    return {"status": "successful", "message": "OK", "code": 204}


@app.post("/comment/update")
def update_comment(data: UpdateComment):
    if db.comments.count_documents({"comment_id": data.comment_id, "author_id": data.author_id}) == 0:
        return {"status": "successful", "message": "User does not have priviledge to update the comment", "code": 401}

    json_data = data.model_dump(mode="json")
    json_data.pop("comment_id")
    json_data.pop("author_id")
    json_data["updated_date"] = datetime.datetime.now()
    json_data = {"$set": json_data}
    try:
        db.comments.update_one({"comment_id": data.comment_id}, json_data)
    except Exception:
        return {"status": "error", "message": "Internal server error", "code": 500}
    return {"status": "successful", "message": "OK", "code": 204}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
