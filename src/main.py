from bot import Bot
import json
import os


def populate_data_dict(path: str):
    with open(path) as f:
        return json.load(f)


JSON_DATA = populate_data_dict(os.environ.get("CONFIG", "/asellibot/configs/config.json"))

bot = Bot(JSON_DATA)
bot.start(os.environ.get('DEV', 'false'))