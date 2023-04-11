from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import DECIMAL
from sqlalchemy import Table
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text

import typing as tp

from src.MarketItem import MarketItem


class Database:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine: tp.Optional[AsyncEngine] = None
        self.meta = MetaData()
        self.items = Table(
            "items",
            self.meta,
            Column("link", String, primary_key=True, nullable=False),
            Column("name", String, nullable=False),
            Column("game_name", String, nullable=False),
            Column("game_id", Integer, nullable=False),
            Column("buy_price", DECIMAL, nullable=False),
            Column("sell_price", DECIMAL, nullable=False),
            Column("buy_orders", Integer, nullable=False),
            Column("sell_orders", Integer, nullable=False)
        )

    async def on_start(self):
        self.engine = create_async_engine(
            self.connection_string,
            pool_size=20,
            max_overflow=10,
        )
        await self.create_database()

    async def on_shutdown(self):
        if self.engine:
            await self.engine.dispose()

    async def create_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.meta.create_all)

    async def drop_databse(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.meta.drop_all)

    async def get_tables_list(self) -> tuple[str]:
        async with self.engine.connect() as conn:
            result = await conn.execute(text('SELECT * FROM information_schema.tables WHERE table_schema = \'public\''))
            result = result.fetchall()
            return tuple((str(i[2]) for i in result))

    async def have_item(self, item: MarketItem) -> bool:
        async with self.engine.connect() as conn:
            cur_item = await conn.execute(select(self.items).where(self.items.c.link == item.link))
            cur_item = cur_item.fetchone()

            if cur_item:
                return True
            return False

    async def get_item(self, item_link: str) -> tp.Optional[MarketItem]:
        async with self.engine.connect() as conn:
            cur_item = await conn.execute(select(self.items).where(self.items.c.link == item_link))
            cur_item = cur_item.fetchone()

            if cur_item:
                return MarketItem.from_tuple(tuple(cur_item))
            return None

    async def get_items(self) -> tuple[MarketItem]:
        async with self.engine.connect() as conn:
            items = await conn.execute(select(self.items))
            items = items.fetchall()
            items = (MarketItem.from_tuple(tuple(i)) for i in items)
            return tuple(items)

    async def insert_item(self, item: MarketItem) -> None:
        async with self.engine.begin() as conn:
            cur_item = await conn.execute(select(self.items).where(self.items.c.link == item.link))
            cur_item = cur_item.fetchone()

            if not cur_item:
                await conn.execute(insert(self.items).values(item.get_database_row()))

    async def insert_items(self, items: tuple[MarketItem]) -> None:
        async with self.engine.begin() as conn:
            items_to_insert = []
            for item in items:
                cur_item = await conn.execute(select(self.items).where(self.items.c.link == item.link))
                cur_item = cur_item.fetchone()

                if not cur_item:
                    items_to_insert.append(item.get_database_row())

            if len(items_to_insert) != 0:
                await conn.execute(self.items.insert().values(items_to_insert))