from sqlite_utils import Database
import dotenv
import json
from rich.pretty import pprint
from rich import inspect
import typer
import aiohttp
import aiorun
import uvloop
from .api import ApiClient

app = typer.Typer()

# for each city, check if there are any items that can be bought and crafted for a profit
# ignore crafting bonuses for now
# 1. get a list of every craftable item
# 2. query the api to get their prices
# 3. for every craftable item, check the profitabiliy of crafting within the city


def is_craftable_item(item: dict) -> bool:
    return "@uniquename" in item and "craftingrequirements" in item


def parse_dict(result: list[dict], subject: dict):
    if is_craftable_item(subject):
        result.append(subject)
        return

    for key, value in subject.items():
        if isinstance(value, dict):
            parse_dict(result, value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    parse_dict(result, item)


def get_craftable_items(items: dict):
    result = list[dict]()
    parse_dict(result, items)
    return result


def get_unique_names(items: dict):
    result = list[str]()
    return result


async def main(loop: uvloop.Loop):
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None))
    api_client = ApiClient(session)
    db = Database("albion.db")
    dotenv.load_dotenv()
    ITEMS_PATH = "/Users/shawnkoh/repos/ao-data/ao-bin-dumps/items.json"
    items_file = open(ITEMS_PATH)
    items_json = json.load(items_file)

    craftable_items = get_craftable_items(items_json)
    pprint(craftable_items)

    craftable_items_uniquename = list()
    for item in craftable_items:
        craftable_items_uniquename.append(item["@uniquename"])

    prices = await api_client.get_prices(craftable_items_uniquename)

    db["prices"].insert_all(
        prices,
        pk=("item_id", "city", "quality"),
        replace=True,
        alter=True,
    )

    # to compute craftable items
    # first, i need to get the sell price of that item

    await session.close()
    loop.stop()


@app.command()
def init():
    loop = uvloop.new_event_loop()
    aiorun.run(main(loop), loop=loop)

    # pprint(craftable_items)
    # pprint(items_json["items"])


# db["items"].insert()