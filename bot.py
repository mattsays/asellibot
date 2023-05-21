from webhook import Webhook
from telebot import *
from jobs import Jobs
import schedule
import time
import threading

class Bot:

    def __init__(self, json):
        self.json = json

        self.tgbot = telebot.TeleBot(json["token"]) # type: ignore        
        self.webhook = Webhook(self, json["token"], json["webhook"])
        self.jobs = Jobs(json)
        # Handlers
        self.tgbot.register_message_handler(callback=self.send_welcome, commands=['start'])
        self.tgbot.register_message_handler(callback=self.send_job, regexp=self.json["cmds"]["job"])
        self.tgbot.register_message_handler(callback=self.send_jobs_week, regexp=self.json["cmds"]["jobs"])
        self.tgbot.register_message_handler(callback=self.send_help, regexp=self.json["cmds"]["help"])
        self.tgbot.register_message_handler(callback=self.send_inhouse_people, regexp=self.json["cmds"]["in_house"])


    def schedule_thread(self):
        schedule.every().monday.at("08:30").do(self.send_jobs_to_all) # Time is in UTC format
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        self.schedThread = threading.Thread(target=self.schedule_thread)
        self.schedThread.start()
        self.webhook.start()

    def commands_markup(self):
        cmds_size = len(self.json["cmds"].values())
        markup = types.ReplyKeyboardMarkup(row_width=int(cmds_size / 2) + (cmds_size % 2))
        for value in self.json["cmds"].values():
            markup.add(types.KeyboardButton(value))
        return markup

    def send_msg(self, message, text, markup = True):
        self.tgbot.send_message(message.chat.id, text, 
                         reply_markup=self.commands_markup() if markup else None)

    def send_msg_to_user(self, username, text, markup = True):
        self.tgbot.send_message(self.json["members"][username]["id"], text, 
                         reply_markup=self.commands_markup() if markup else None)
     
    def send_welcome(self, message):
        if(message.chat.username in self.json["members"].keys()):
            self.send_msg(message, 
            "Ciao benvenuto! \n " +
            "Questo bot e stato pensato per aiutare i coinquilini che sono ritardati. \n" + 
            "Gli ideatori del bot @mattsays e @filippoGalliCr sono persone stupide, quindi in caso di errori o bug, attacati al cazzo.\n" +
            "Bene, da ora in poi ogni lunedi ti manderò il tuo cazzo di turno pezzo di merda. Dopo aver stabilito le regole di base ecco le mie features:", 
            )
        else:
            self.send_msg(message, "Sei una merda umana, non sei della Aselli Crew! VATTENE!", markup=True)

    def send_job(self, message):
        if(message.chat.username in self.json["members"].keys()):
            self.send_msg(message, f"Ecco il tuo turno bestia:\n{self.jobs.getWeekJob(message.chat.username)}\nOra vedi di muoverti che non fai mai un cazzo.")
        else:
            self.send_msg(message, "Sei una merda umana, vai via bastardo!")
            
    def send_jobs_week(self, message):
        if(message.chat.username not in self.json["members"].keys()):
            self.send_msg(message, f"Muori..")
            return
        self.send_msg(message, "Ecco i cazzi degli altri\n")
        jobs = self.jobs.getWeekJobs()
        jobs_str = ''
        for job in jobs.items():
            jobs_str += f"{job[0]}: {job[1]}\n"
        self.send_msg(message, jobs_str)
        self.send_msg(message, "Ora torna a lavorare che cazzeggi sempre.")

    def send_jobs_to_all(self):
        jobs = self.jobs.getWeekJobs()
        for username in self.json["members"].keys():
            job = jobs[self.json["members"][username]["display_name"]]
            self.send_msg_to_user(username, f"Bungiorno la tua mansione della settimana è \"{job}\"", markup = False)

    def send_inhouse_people(self, message):
        if(message.chat.username in self.json["members"].keys()):
            self.send_msg(message, f"We spione qua ci sono:")
            for person in self.inhouse:
                self.send_msg(message, f"{self.json['members'][person]['display_name']}")
        else:
            self.send_msg(message, "Sei una merda umana, vai via bastardo!", markup = False)
      
    def in_house_update(self, people):
        self.inhouse = people["in_house"]

    def send_help(self, message):
        self.send_welcome(message)
