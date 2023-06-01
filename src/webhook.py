import fastapi
import uvicorn
import telebot
import bot
import time
import os

class Webhook:

    def __init__(self, bot, token, json):
        self.app = fastapi.FastAPI(docs=None, redoc_url=None)
        self.bot = bot
        self.token = token
        self.json = json

        self.app.add_api_route(path=f'/{token}/', 
                               endpoint=self.process_webhook, 
                               methods=["POST"])
        
        self.app.add_api_route(path=f'/{token}/in_house/', 
                               endpoint=self.process_update_people_list, 
                               methods=["POST"])


    def process_webhook(self, update: dict):
        """
        Process webhook calls
        """
        if update:
            update = telebot.types.Update.de_json(update)
            self.bot.tgbot.process_new_updates([update])
        else:
            return

    def process_update_people_list(self, people: dict):
        """
        Handles inhouse counter updates
        """
        if people:
            self.bot.in_house_update(people)
        else:
            return

    def start(self):
        
        self.bot.tgbot.remove_webhook()

        base_url = f"https://{ self.json['host'] }:{ self.json['port'] }"
        url_path = f"/{self.token}/"
        # Set webhook
        self.bot.tgbot.set_webhook(
            url=base_url + url_path
        )

        uvicorn.run(
            self.app,
            host='0.0.0.0',
            port=self.json["port"],
            ssl_certfile=os.environ["SSL_CERT"],
            ssl_keyfile=os.environ["SSL_KEY"]
        )
