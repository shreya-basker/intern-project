from fastapi import FastAPI
from pydantic import BaseModel
user_db={
    1: {
        "id": 1,
        "name": "Shreya",
        "email": "shreya@gmail.com",
        "active": True
    },
    2: {
        "id": 2,
        "name": "Basker",
        "email": "basker@gmail.com",
        "active": True
    },
    3: {
        "id": 3,
        "name": "Pankajam",
        "email": "panki@gmail.com",
        "active": True
    }
}
Class User(BaseModel):

app=FastAPI()
