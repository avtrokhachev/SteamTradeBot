import time

from copy import copy

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import bs4

import logging

from MarketItem import MarketItem

from functions import convert_to_dollars


class Parser:
    market_link = "https://steamcommunity.com/market/search?appid=%s#p%s_price_asc"
    time_to_wait = 5
    time_timeout = 120
    time_to_load = 1

    def __init__(self, game_id: int):
        self.game_id: int = game_id

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        self.driver = webdriver.Chrome('chromedriver', options=options)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        py_handler = logging.FileHandler(f"{__name__}.log", mode='a')
        py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
        py_handler.setFormatter(py_formatter)
        self.logger.addHandler(py_handler)

        self.logger.info(f"Parser for game with game_id = {self.game_id} created")

    def get_total_pages(self) -> int:
        link = Parser.market_link % (self.game_id, 1)
        self.logger.info(f"Getting number of pages for game_id = {self.game_id} by link {link}")

        while True:
            try:
                self.driver.get(link)
                WebDriverWait(self.driver, Parser.time_to_load).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'market_paging_pagelink.active')))

                self.logger.info(f"Page {link} successfully loaded")
                soup = bs4.BeautifulSoup(self.driver.page_source, "html.parser")
                all_pages = soup.find_all("span", {"class": "market_paging_pagelink"})
                all_pages.extend(soup.find_all("span", {"class": "market_paging_pagelink.active"}))
                all_pages = [int(i.text) for i in all_pages]
                all_pages.sort()
                numer_of_pages = all_pages[-1]

                self.logger.info(f"Got number of pages {numer_of_pages} for game_id = {self.game_id}")
                return numer_of_pages
            except TimeoutException as timeout:
                self.logger.warning(f"Timeout occurred for game_id = {self.game_id}, link = {link}")
                time.sleep(Parser.time_timeout)
            except Exception as e:
                self.logger.exception(e)
                time.sleep(Parser.time_timeout)

    def get_items_from_page(self, page_number: int) -> list[MarketItem]:
        link = Parser.market_link % (self.game_id, page_number)
        self.driver.delete_all_cookies()
        self.logger.info(f"Getting items from page = {page_number} for game_id = {self.game_id} by link {link}")

        while True:
            try:
                self.driver.get(link)
                WebDriverWait(self.driver, Parser.time_to_wait).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'market_sortable_column')))

                self.logger.info(f"Page {link} successfully loaded")
                time.sleep(Parser.time_to_load)
                soup = bs4.BeautifulSoup(self.driver.page_source, "html.parser")
                raw_items = soup.find_all("a", {"class" : "market_listing_row_link"})
                items = [MarketItem.from_raw_html(i, self.game_id) for i in raw_items]
                self.logger.info(f"Got {len(items)} items from page = {page_number}, link = {link}")
                return items
            except TimeoutException:
                self.logger.warning(f"Timeout occurred for game_id = {self.game_id}, link = {link}")
                time.sleep(Parser.time_timeout)

    def get_all_items(self) -> list[MarketItem]:
        self.logger.info(f"Start getting all items for game_id = {self.game_id}")
        max_pages = self.get_total_pages()
        current_page = 1

        while current_page <= max_pages:
            items_on_page = self.get_items_from_page(current_page)
            if len(items_on_page) != 0:
                for i in items_on_page:
                    yield i
                current_page += 1
            time.sleep(Parser.time_to_wait)

    def get_cost_and_orders(self, item: MarketItem) -> MarketItem:
        self.logger.info(f"Getting info for item {item.name}, link {item.link}")
        new_item = copy(item)
        self.driver.delete_all_cookies()

        while True:
            try:
                self.driver.get(new_item.link)
                WebDriverWait(self.driver, Parser.time_to_wait).until(
                    EC.presence_of_element_located((By.ID, 'market_commodity_forsale')))
                WebDriverWait(self.driver, Parser.time_to_wait).until(
                    EC.presence_of_element_located((By.ID, 'market_commodity_buyrequests')))

                self.logger.info(f"Page {new_item.link} successfully loaded")
                time.sleep(Parser.time_to_load)
                soup = bs4.BeautifulSoup(self.driver.page_source, "html.parser")
                sales = soup.find("div", {"id" : "market_commodity_forsale"})
                raw_text = sales.find_all("span", {"class" : "market_commodity_orders_header_promote"})
                new_item.sell_orders = int(raw_text[0].text)
                new_item.sell_price = convert_to_dollars(raw_text[1].text)

                sales = soup.find("div", {"id": "market_commodity_buyrequests"})
                raw_text = sales.find_all("span", {"class": "market_commodity_orders_header_promote"})
                new_item.buy_orders = int(raw_text[0].text)
                new_item.buy_price = convert_to_dollars(raw_text[1].text)
                break
            except TimeoutException:
                self.logger.warning(f"Timeout occurred for item {new_item.name}, link {new_item.link}")
                time.sleep(Parser.time_timeout)
            except Exception as e:
                self.logger.exception(e)
                time.sleep(Parser.time_timeout)

        self.logger.info(f"Successfully got info for {new_item.name}")
        time.sleep(Parser.time_to_wait)
        return new_item

    def get_balance(self) -> float:
        # TODO
        return 100.0
