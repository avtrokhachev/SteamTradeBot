from src.MarketBot import MarketBot

import asyncio

from src.functions import get_settings


async def main():
    config = get_settings()
    bot = MarketBot(252490, config)
    await bot.start()
    await bot.get_the_worthest_item()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
