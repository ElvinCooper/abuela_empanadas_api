import asyncio
import asyncpg

async def check():
    conn = await asyncpg.connect(host='127.0.0.1', port=5433, user='postgres', password='postgres', ssl=False)
    rows = await conn.fetch('SELECT datname FROM pg_database')
    for r in rows:
        print(r['datname'])
    await conn.close()

asyncio.run(check())