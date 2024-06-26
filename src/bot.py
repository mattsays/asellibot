from pydantic import BaseModel
from webhook import Webhook
from telebot import *
from telebot import formatting
from jobs import Jobs
import schedule
import time
import threading
import random
from scapy.all import srp,Ether,ARP,conf 
import os
import json

class InHousePerson(BaseModel):
    username: str
    connected_devices: List[str]
    devices: List[str]
    last_update_time: int

class FoodTurn(BaseModel):
    username: str
    pickUp: bool

class Bot:
    started: bool
    json: dict
    inhouse: List[InHousePerson]
    update_interval: int
    tgbot: TeleBot
    webhook: Webhook
    logger: logging.Logger
    jobs: Jobs
    
    def __init__(self, json):
        self.json = json
        self.inhouse: List[InHousePerson] = []
        self.foodPickup: List[FoodTurn] = []
        self.update_interval = self.json['inhouse_update_interval']        
        self.logger = logging.getLogger(__name__)
        self.tgbot = telebot.TeleBot(json["token"])  # type: ignore
        self.webhook = Webhook(self, json["token"], json["webhook"])
        self.jobs = Jobs(json)
        
        # Handlers
        self.tgbot.register_message_handler(
            callback=self.send_welcome, commands=["start"]
        )
        self.tgbot.register_message_handler(
            callback=self.send_job, regexp=self.json["cmds"]["job"]
        )
        self.tgbot.register_message_handler(
            callback=self.send_jobs_week, regexp=self.json["cmds"]["jobs"]
        )
        self.tgbot.register_message_handler(
            callback=self.send_help, regexp=self.json["cmds"]["help"]
        )
        self.tgbot.register_message_handler(
            callback=self.turn_of_getting_food, regexp=self.json["cmds"]["turn_of_getting_food"],
        )
        
        self.tgbot.register_message_handler(
            callback=self.send_inhouse_people, regexp=self.json["cmds"]["in_house"]
        )
        
        self.started = True

    def update_state(self):
        with open(os.environ.get("CONFIG", "/asellibot/configs/config.json")) as f:
            self.json = json.load(f)
        
        for username, data in self.json["members"].items():
            self.inhouse.append(InHousePerson(username=username, 
                                       connected_devices=[], 
                                       last_update_time=0,
                                       devices=data['mac_addresses']))
            self.foodPickup.append(FoodTurn(username=username,
                                            pickUp=data['food_pickup']))


    def schedule_thread(self):
        schedule.every().monday.at("08:30").do(
            self.send_jobs_to_all
        )  # Time is in UTC format
        
        while self.started:
            self.update_connected_people()
            schedule.run_pending()
            time.sleep(1)

    def start(self, dev_mode: str = 'false'):
        self.schedThread = threading.Thread(target=self.schedule_thread)
        self.schedThread.start()
        
        if dev_mode == 'true':
            print('Starting bot..')
            self.tgbot.delete_webhook()
            self.tgbot.infinity_polling()
        else:  
            self.webhook.start()
    
    def update_connected_people(self):
        needs_update = False
        
        for person in self.inhouse:
            if time.time() - person.last_update_time >= self.update_interval or \
                len(person.connected_devices) == 0:
                    needs_update = True
                    break
        
        if not needs_update:
            return
        
        curr_devices = []
        conf.verb = 0 
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst = '192.168.1.0/24'), 
		     timeout = 2, 
		     iface = 'eth0',
		     inter = 0.1)
        for _,rcv in ans: 
            curr_devices.append(rcv.sprintf(r"%Ether.src%"))

        for person in self.inhouse:
            if time.time() - person.last_update_time >= self.update_interval or \
                len(person.connected_devices) == 0:
                    person.connected_devices = [device for device in curr_devices if device in person.devices]
                    person.last_update_time = time.time()

    def get_connected_people(self):
        return [person.username for person in self.inhouse if len(person.connected_devices) > 0]

    def commands_markup(self):
        cmds_size = len(self.json["cmds"].values())
        markup = types.ReplyKeyboardMarkup(
            row_width=int(cmds_size / 2) + (cmds_size % 2)
        )
        for value in self.json["cmds"].values():
            markup.add(types.KeyboardButton(value))
        return markup
    
    def send_msg(self, message, text, markup=True):
        self.tgbot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='MarkdownV2',
            reply_markup=self.commands_markup() if markup else None,
        )
        
    def send_welcome(self, message):
        if message.chat.username in self.json["members"].keys():
            self.send_msg(
                message,
                "Ciao benvenuto\! \n "
                + "Questo bot e stato pensato per aiutare i coinquilini che sono ritardati\. \n"
                + "Gli ideatori del bot @mattsays e @filippoGalliCr sono persone stupide, quindi in caso di errori o bug, attacati al cazzo\.\n"
                + "Bene, da ora in poi ogni lunedi ti manderò il tuo cazzo di turno pezzo di merda\. Dopo aver stabilito le regole di base ecco le mie features:",
            )
        else:
            self.send_msg(
                message,
                "Sei una merda umana, non sei della Aselli Crew\! VATTENE\!",
                markup=True,
            )

    def send_job(self, message):
        if message.chat.username in self.json["members"].keys():
            self.send_msg(
                message,
                f"Ecco il tuo turno bestia:\n{self.jobs.getWeekJob(message.chat.username)}\nOra vedi di muoverti che non fai mai un cazzo\.",
            )
        else:
            self.send_msg(message, "Sei una merda umana, vai via bastardo\!")

    def send_jobs_week(self, message):
        if message.chat.username not in self.json["members"].keys():
            self.send_msg(message, "Muori\.\.")
            return
        jobs = self.jobs.getWeekJobs()
        jobs_str = "Ecco i cazzi degli altri: \n\n"
        for job in jobs.items():
            jobs_str += f"*{job[0]}*: {job[1]}\n" 
        jobs_str += "\nOra torna a lavorare che cazzeggi sempre\."
        self.send_msg(message, jobs_str)

    def send_jobs_to_all(self):
        jobs = self.jobs.getWeekJobs()
        for username in self.json["members"].keys():
            job = jobs[self.json["members"][username]["display_name"]]            
            self.tgbot.send_message(
                chat_id=self.json["members"][username]['id'],
                text=f'Bungiorno la tua mansione della settimana è "{job}"',
                parse_mode='MarkdownV2',
                reply_markup=None,
            )

    def send_inhouse_people(self, message):
        if message.chat.username in self.json["members"].keys():
            if len(self.get_connected_people()) == 0:
                self.send_msg(message, 'Pezzo di merda la casa è vuota\.')
                return
            str_mex = "Ecco chi c'è in casa:\n"
            for person in self.get_connected_people():
                str_mex += f"*{self.json['members'][person]['display_name']}*\n"
            self.send_msg(message, str_mex)
        else:
            self.send_msg(
                message, "Sei una merda umana, vai via bastardo\!", markup=False
            )

    def send_help(self, message):
        self.send_welcome(message)
    
    def updateJSON_foodPickup(self, possible_person: List, reset: bool = False):
        # reset to True every member after a cycle was done
        if reset == False:            
            # set to false the one already go down
            self.json["members"][possible_person[0]]['food_pickup'] = False
            
        else: 
            for username, data in self.json["members"].items():
                if username in possible_person:
                    data['food_pickup'] = True

        # write the changes on the json
        with open(os.environ.get("CONFIG", "/asellibot/configs/config.json"), 'w') as file:
            json.dump(self.json, file, indent=4)
        
        # Update self.foodPickup
        for username, data in self.json["members"].items():
            for person in self.foodPickup:
                if(person.username == username):
                    person.pickUp = data["food_pickup"]
        
    def turn_of_getting_food(self, message):
        # Function to decide who is going to get food
        if message.chat.username in self.json["members"].keys():
            connected_people = self.get_connected_people()
            if len(connected_people) == 0:
                    self.send_msg(message, 'Pezzo di merda la casa è vuota\.')
                    return
            
            self.update_state()
            
            possible_person = []
            err = True

            for person in self.foodPickup:
                if(person.pickUp == True and person.username in connected_people):
                    possible_person.append(person.username)
                    err = False

            # if all people are false
            if err == True:
                self.updateJSON_foodPickup(connected_people, True)
                possible_person = connected_people


            random.shuffle(possible_person)

            self.updateJSON_foodPickup(possible_person)

            self.send_msg(
                message, f"Stasera scende a prendere il cibo: *{self.json['members'][possible_person[0]]['display_name']}*"
            )
        else:
            self.send_msg(
                message, "Schifo, FAI SCHIFO\!", markup=False
            )