import asyncio

import asyncpg


async def insert_user(name, email, age):
    conn = await asyncpg.connect(
        host="localhost", port=5432, user="intern", password="intern123", database="intern_db"
    )
    try:
        new_id = await conn.fetchval(
            """
        INSERT INTO users(name,email,age)
        VALUES($1, $2, $3)
        RETURNING id
        """,
            name,
            email,
            age,
        )
        print(f"insert_user: Inserted user with id: {new_id}")
        return new_id
    except asyncpg.UniqueViolationError:
        print("User already exists with the same email.")
    finally:
        await conn.close()


async def task1():
    conn = await asyncpg.connect(
        host="localhost", port=5432, user="intern", password="intern123", database="intern_db"
    )
    rows = await conn.fetch(
        """
    SELECT *
    FROM users
    WHERE age > $1
    """,
        28,
    )
    for row in rows:
        print(dict(row))
    await conn.close()


async def main():
    user_id = await insert_user("Shreya", "shreya.basker@gmail.com", 25)
    print(f"Inserted user with id: {user_id}")
    await insert_user("Shreya Basker", "shreya.basker@gmail.com", 25)


asyncio.run(main())
