import datetime
from uuid import uuid4
from random import choice, choices

import bcrypt
from faker import Faker
from pymongo import MongoClient

from config import MONGO_CREDS, HASH_SALT

fake = Faker()
db = MongoClient(**MONGO_CREDS)["blogpost"]

db.drop_collection("users")
db.drop_collection("blogs")
db.drop_collection("comments")

raise KeyError()
# create fake users
user_ids = []
for _ in range(100):
    id_, name = str(uuid4()), fake.name()
    email = name.replace(" ", "").replace(".", "") + "@xyz.com"
    db.users.insert_one({"user_id": id_, "username": name, "email": email,
                         "password": bcrypt.hashpw(email.encode('utf-8'), HASH_SALT).decode('utf8'),
                         "registered_date": datetime.datetime.now()})
    user_ids.append(id_)
print("Inserted users")

# create fake blogs
sample_tags = ["tech", "python", "windows", "door", "furniture"]
sample_categories = ["tech", "finance", "lifestyle", "home"]
blog_ids = []
for _ in range(50):
    id_ = str(uuid4())
    user_id = choice(user_ids)
    content = fake.text()
    title = content[:50]

    db.blogs.insert_one({"author_id": user_id, "title": title, "content": content,
                         "tags": choices(sample_tags, k=2), "categories": choices(sample_categories, k=1),
                         "created_date": datetime.datetime.now(), "blog_id": id_})
    blog_ids.append(id_)
print("Inserted blogs")

# create fake comments
for _ in range(200):
    user_id = choice(user_ids)
    blog_id = choice(blog_ids)

    user = list(db.users.find({"user_id": user_id}))[0]
    db.comments.insert_one({"author_id": user_id, 'content': fake.text()[:150], "username": user["username"],
                           "blog_id": blog_id, "created_date": datetime.datetime.now()})

print("Inserted comments")
