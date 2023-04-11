
import asyncpg

import typing as tp

from MarketItem import MarketItem


class Database:

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.db: tp.Optional[asyncpg.Pool] = None

    async def on_start(self):
        self.db = await asyncpg.create_pool(self.connection_string)
        await self.create_database()

    async def on_shutdown(self):
        if self.db:
            await self.db.close()

    async def create_database(self):
        async with self.db.acquire() as con:
            await con.execute('''
            CREATE TABLE IF NOT EXISTS items( 
            link TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            game_name TEXT NOT NULL,
            game_id INTEGER NOT NULL,
            buy_price DECIMAL NOT NULL,
            sell_price DECIMAL NOT NULL,
            buy_orders INTEGER NOT NULL,
            sell_orders INTEGER NOT NULL
            )
            ''')

    async def have_item(self, con: asyncpg.Connection, item: MarketItem) -> bool:
        cur_item = await con.fetchrow("""
                SELECT * FROM items
                WHERE link = $1            
                """, item.link)
        if cur_item:
            return True
        return False

    async def get_items(self) -> tuple[MarketItem]:
        async with self.db.acquire() as con:
            items = await con.fetch("""
                    SELECT * FROM items
            """)
            items = tuple(items)
            items = [MarketItem.from_tuple(i) for i in items]
            return tuple(items)

    async def insert_item(self, item: MarketItem):
        async with self.db.acquire() as con:
            if not await self.have_item(con, item):
                await con.copy_records_to_table('items', records=[item.get_database_row()])
