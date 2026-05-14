import asyncio
from database import db


async def main():
    await db.init_db()
    rows = await db.fetch("SELECT DISTINCT username FROM radcheck ORDER BY username;")
    print(rows)
    await db.close_db()


asyncio.run(main())