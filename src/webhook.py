import fastapi
import uvicorn
import telebot
import time
import os
from contextlib import asynccontextmanager


class Webhook:
    def __init__(self, bot, token, json):
        self.app = fastapi.FastAPI(docs=None, redoc_url=None)
        self.bot = bot
        self.token = token
        self.json = json

        self.app.add_api_route(
            path=f"/{token}/", endpoint=self.process_webhook, methods=["POST"]
        )

    def process_webhook(self, update: dict):
        """
        Process webhook calls
        """
        if update:
            update = telebot.types.Update.de_json(update)
            self.bot.tgbot.process_new_updates([update])
        else:
            return

    @asynccontextmanager
    async def lifespan(self, app: fastapi.FastAPI):
        yield
        print('Stopping..')
        self.bot.started = False
        self.bot.schedThread.join()

    def start(self):
        self.bot.tgbot.remove_webhook()

        base_url = f"https://{ self.json['host']}"
                
        url_path = f"/{self.token}/"
        # Set webhook
        self.bot.tgbot.set_webhook(url=base_url + url_path)

        self.app.router.lifespan_context = self.lifespan
        
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=self.json["port"],
            ssl_certfile=self.json["ssl_cert"] if self.json["ssl_cert"] != '' else None,
            ssl_keyfile=self.json["ssl_key"]  if self.json["ssl_key"] != '' else None,
        )
