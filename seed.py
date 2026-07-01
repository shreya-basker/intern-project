import asyncio

from week4.app.database import AsyncSessionLocal
from week4.app.models import User
from week4.app.security import hash_password

SEEDS = [
    {"name": "Admin User", "email": "admin@test.com", "role": "admin", "password": "Test1234!"},
    {"name": "Editor User", "email": "editor@test.com", "role": "editor", "password": "Test1234!"},
    {"name": "Viewer User", "email": "viewer@test.com", "role": "viewer", "password": "Test1234!"},
]


async def seed():
    async with AsyncSessionLocal() as db:
        for s in SEEDS:
            user = User(
                name=s["name"],
                email=s["email"],
                role=s["role"],
                hashed_password=hash_password(s["password"]),
            )
            db.add(user)
        await db.commit()
        print("Seeded 3 test accounts.")


asyncio.run(seed())
