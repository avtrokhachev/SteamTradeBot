from src.MarketItem import MarketItem

from random import randint
from random import random


def generate_random_word() -> str:
    word = []
    for i in range(randint(1, 100)):
        word.append(chr(ord('a') + randint(0, 25)))
    return ''.join(word)


def generate_random_items(n: int) -> tuple[MarketItem]:
    ans = []
    for i in range(n):
        item = MarketItem(
            "link" + str(i),
            generate_random_word(),
            generate_random_word(),
            randint(0, 10**9),
            random(),
            random(),
            randint(0, 10**5),
            randint(0, 10**5)
        )
        ans.append(item)

    return tuple(ans)
