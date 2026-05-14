import os
import logging
import aiomysql
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

pool = None

async def init_db():
    global pool
    try:
        pool = await aiomysql.create_pool(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
            autocommit=True
        )
        log.info("DB pool initialized")
    except Exception:
        log.exception("Failed to initialize DB pool")
        raise

async def fetch(query, params=None):
    if pool is None:
        raise RuntimeError("DB pool not initialized")
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, params)
            return await cur.fetchall()

async def close_db():
    global pool
    if pool is None:
        return
    pool.close()
    await pool.wait_closed()
    pool = None
    log.info("DB pool closed")

async def execute(query, params=None):
    if pool is None:
        raise RuntimeError("DB pool not initialized")
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, params)
            try:
                return cur.lastrowid
            except Exception:
                return cur.rowcount