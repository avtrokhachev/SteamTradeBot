from configparser import SectionProxy

from Parser import Parser

from Database import Database

import typing as tp

from MarketItem import MarketItem


class MarketBot:
    def __init__(self, game_id: int, cfg: SectionProxy):
        self.game_id: int = game_id
        self.parser = Parser(game_id)
        self.balance: float = self.parser.get_balance()
        self.database = Database(cfg["PostgresOptions"])

    async def start(self):
        await self.database.on_start()

    async def update_items(self):
        for i in self.parser.get_all_items():
            i = self.parser.get_cost_and_orders(i)
            await self.database.insert_item(i)

    async def get_the_worthest_item(self) -> tp.Optional[MarketItem]:
        items = await self.database.get_items()
        items = list(items)
        items = [(MarketItem.get_worth(i), i) for i in items]
        items.sort(key=lambda x: x[0])
        items.reverse()
        if items[0][0] > 0:
            return items[0][1]
        return None

