import datetime
from hashlib import md5
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

# create fake users
user_ids = []
for _ in range(100):
    id_, name = str(uuid4()), fake.name()
    email = name.replace(" ", "").replace(".", "") + "@xyz.com"
    db.users.insert_one({"user_id": id_, "username": name.lower().replace(" ", ""), "email": email,
                         "first_name": name.split(" ")[0],
                         "last_name": name.split(" ")[1], "password": md5(email.encode("utf8")).hexdigest(),
                         "registered_date": datetime.datetime.now()})
    user_ids.append(id_)
print("Inserted users")

# create fake blogs
sample_maps = {"tech": ["python", "java", "devops", "dynamic programming"],
               "finance": ["stock market", "options", "accounting"]}
blog_ids = []
for _ in range(50):
    id_ = str(uuid4())
    user_id = choice(user_ids)
    content = fake.text()
    title = content[:50]
    category = choice(list(sample_maps.keys()))
    tags = choices(sample_maps[category], k=2)

    db.blogs.insert_one({"author_id": user_id, "title": title, "content": content,
                         "tags": tags, "categories": [category],
                         "created_date": datetime.datetime.now(), "blog_id": id_})
    blog_ids.append(id_)
print("Inserted blogs")

# create fake comments
for _ in range(200):
    user_id = choice(user_ids)
    blog_id = choice(blog_ids)
    comment_id = str(uuid4())

    user = list(db.users.find({"user_id": user_id}))[0]
    db.comments.insert_one({"author_id": user_id, 'content': fake.text()[:150], "comment_id": comment_id,
                           "blog_id": blog_id, "created_date": datetime.datetime.now()})

print("Inserted comments")
