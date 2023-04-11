from __future__ import annotations

from dataclasses import dataclass

import typing as tp

import bs4

COMMISION = 0.13


@dataclass
class MarketItem:

    link: str
    name: str
    game_name: str
    game_id: int
    buy_price: tp.Optional[float] = None
    sell_price: tp.Optional[float] = None
    buy_orders: tp.Optional[int] = None
    sell_orders: tp.Optional[int] = None

    @classmethod
    def from_raw_html(cls, raw_html: bs4.element.PageElement, game_id: int) -> MarketItem:
        item_link = raw_html['href']
        context = raw_html.find_next('div', {'class' : 'market_listing_item_name_block'})
        item_name = context.find_next('span', {'class' : 'market_listing_item_name'}).text
        item_game = context.find_next('span', {'class' : 'market_listing_game_name'}).text
        return cls(item_link, item_name, item_game, game_id)

    @classmethod
    def from_tuple(cls, data: tuple) -> MarketItem:
        return cls(data[0], data[1], data[2], data[3], float(data[4]), float(data[5]), data[6], data[7])

    def get_database_row(self) -> tuple:
        return self.link, self.name, self.game_name, self.game_id, self.buy_price, self.sell_price, self.buy_orders,\
            self.sell_orders

    def get_worth(self) -> tp.Optional[float]:
        if not self.buy_orders or not self.sell_orders or not self.buy_price or not self.sell_price:
            raise Exception(f"Order {self.link} wasn't filled with info before get_worth action")

        total_earn = self.sell_price * (1 - COMMISION) - self.buy_price
        if total_earn <= 0.5 or total_earn / self.buy_price < 0.1:
            return None
        if self.buy_orders < self.sell_orders * 8:
            return None
        return total_earn / self.buy_price

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result









