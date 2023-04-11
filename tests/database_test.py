import pytest

from src.Database import Database

from src.MarketItem import MarketItem

from src.functions import get_settings

from functions import generate_random_items


@pytest.fixture
@pytest.mark.asyncio
async def prepare_database() -> Database:
    settings = get_settings()
    database = Database(settings["PostgresOptions"])
    await database.on_start()

    await database.drop_databse()
    await database.create_database()

    return database


@pytest.mark.asyncio
async def test_database_creating(prepare_database):
    database = await prepare_database

    assert len(await database.get_tables_list()) == 1
    assert "items" in await database.get_tables_list()


@pytest.mark.asyncio
async def test_database_deleting(prepare_database):
    database = await prepare_database

    await database.drop_databse()
    assert len(await database.get_tables_list()) == 0


@pytest.mark.parametrize('items', [
    [],
    [MarketItem("link1", "first", "Rust", 123, 0, 0, 0, 0)],
    [
        MarketItem("link1", "first", "Rust", 123, 0, 0, 0, 0),
        MarketItem("link2", "second", "Rust", 123, 1, 2, 3, 4),
        MarketItem("link3", "third", "Rust", 123, 5, 0, 3, 0),
        MarketItem("link4", "second", "Rust", 123, 1, 1, 1, 1)
    ]
])
@pytest.mark.asyncio
async def test_database_inserting(prepare_database, items):
    database = await prepare_database
    for i in items:
        await database.insert_item(i)

    all_items = await database.get_items()
    assert len(all_items) == len(items)

    for i in items:
        assert await database.have_item(i)


@pytest.mark.parametrize('n', [
    0, 1, 4, 10, 10**2, 10**2+5, 10**2 + 7
])
@pytest.mark.asyncio
async def test_database_inserting_random(prepare_database, n):
    database = await prepare_database
    items = generate_random_items(n)

    for i in items:
        await database.insert_item(i)

    all_items = await database.get_items()
    assert len(all_items) == len(items)

    for i in items:
        assert await database.have_item(i)


@pytest.mark.parametrize('items', [
    [],
    [MarketItem("link1", "first", "Rust", 123, 0, 0, 0, 0)],
    [
        MarketItem("link1", "first", "Rust", 123, 0, 0, 0, 0),
        MarketItem("link2", "second", "Rust", 123, 1, 2, 3, 4),
        MarketItem("link3", "third", "Rust", 123, 5, 0, 3, 0),
        MarketItem("link4", "second", "Rust", 123, 1, 1, 1, 1)
    ]
])
@pytest.mark.asyncio
async def test_database_inserting_many(prepare_database, items):
    database = await prepare_database
    await database.insert_items(tuple(items))

    all_items = await database.get_items()
    assert len(all_items) == len(items)

    for i in items:
        assert await database.have_item(i)


@pytest.mark.parametrize('n', [
    0, 1, 4, 10, 10**2, 10**3+5, 10**3, 3*10**3
])
@pytest.mark.asyncio
async def test_database_inserting_many_random(prepare_database, n):
    database = await prepare_database
    items = generate_random_items(n)

    await database.insert_items(tuple(items))

    all_items = await database.get_items()
    assert len(all_items) == len(items)


@pytest.mark.parametrize('items', [
    [],
    [MarketItem("link1", "first", "Rust", 123, 0, 0, 0, 0)],
    [
        MarketItem("link1", "first", "Rust", 123, 0, 0, 0, 0),
        MarketItem("link2", "second", "Rust", 123, 1, 2, 3, 4),
        MarketItem("link3", "third", "Rust", 123, 5, 0, 3, 0),
        MarketItem("link4", "second", "Rust", 123, 1, 1, 1, 1)
    ]
])
@pytest.mark.asyncio
async def test_get_items(prepare_database, items):
    database = await prepare_database
    await database.insert_items(tuple(items))

    for i in items:
        item = await database.get_item(i.link)
        assert item == i


@pytest.mark.parametrize('n', [
    0, 1, 4, 10, 10**2, 10**3+5, 10**3, 3*10**3
])
@pytest.mark.asyncio
async def test_get_items_random(prepare_database, n):
    database = await prepare_database
    items = generate_random_items(n)

    await database.insert_items(tuple(items))

    for i in items:
        item = await database.get_item(i.link)
        assert item == i

