from bot import Bot
import json

def populate_data_dict(path: str):
    with open(path) as f:
        return json.load(f)


JSON_DATA = populate_data_dict('./config.json')

bot = Bot(JSON_DATA)
bot.start()