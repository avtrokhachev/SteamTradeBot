import configparser

import os

from MarketBot import MarketBot

import asyncio


def get_settings() -> configparser.SectionProxy:
    in_container = os.environ.get('IN_A_DOCKER_CONTAINER', False)
    sect = "Container" if in_container else "Development"
    path = '../Settings.ini'
    if os.path.isfile("Settings.ini"):
        path = "Settings.ini"

    parser = configparser.ConfigParser()
    parser.read(path)
    return parser[sect]


async def main():
    config = get_settings()
    bot = MarketBot(252490, config)
    await bot.start()
    await bot.get_the_worthest_item()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
