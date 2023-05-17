from telebot import *
import schedule
import time
import threading
from datetime import date, datetime
from dateutil import rrule
from os import environ as env
import re

# Constants
BOT_TIMEOUT = 30

# The BigBang
START_DATE = datetime.strptime("10/10/2022", "%d/%m/%Y").date()
# Base jobs for start date: 
# Filippo : Bagno (0)
# Mattia : Pavimenti (1)
# Michele : Cucina (2)
FIRST_INDICES = {'Filippo': 0, 'Mattia': 1, 'Michele': 2}
JOB_TYPES = ["Bagno 🚽", "Pavimenti 🧹", "Piano cottura e Bidoni 🔥/🗑️"]
users = {
	"mattsays": ["Mattia"],
	"filippoGalliCr": ["Filippo"],
	"Michelepave": ["Michele"]
}



# Text commands

TEXTS = {
		"JOB_TEXT": 'Sono in vena di pulizie',
		"JOBS_TEXT": 'Voglio spiare gli altri',
		"HELP_TEXT": 'Help'
}

run = True

# Weekly calculated jobs

def initializeChatIds():
	chat_id_file = open("chat_id.txt", 'r')
	lines = chat_id_file.readlines()
	for line in lines:
		[name, id] = line.split(":")
		id = id.strip() # removing spaces and abnormal chars
		users[name].append(id)

def getWeekIndex():
	weeks = rrule.rrule(rrule.WEEKLY, dtstart=START_DATE, until=date.today())
	return (weeks.count() - 1) % 3

def getWeekJobs():
	week_index = getWeekIndex()
	jobs = {
		"Filippo": JOB_TYPES[(0 + week_index) % 3],
		"Mattia": JOB_TYPES[(1 + week_index) % 3],
		"Michele": JOB_TYPES[(2 + week_index) % 3]
	}
	return jobs

def getWeekJob(name):
	week_index = getWeekIndex()
	return JOB_TYPES[(FIRST_INDICES[name] + week_index) % 3]

def getNextWeekJob(name):
	week_index = getWeekIndex() + 1
	return JOB_TYPES[(FIRST_INDICES[name] + week_index) % 3]

# Telegram related part

bot = telebot.TeleBot(env["YOUWASH_TOKEN"], parse_mode=False) # type: ignore

def commands_markup():
	markup = types.ReplyKeyboardMarkup(row_width=2)
	for value in TEXTS.values():
		markup.add(types.KeyboardButton(value))
	return markup

def send_msg(message, text, markup = None):
	bot.send_message(message.chat.id, text, reply_markup=markup)

def cleaning_msg():
	jobs = getWeekJobs()
	for user_data in users.values():
		if(len(user_data) != 2):
			continue
		bot.send_message(user_data[1], f"Bungiorno la tua mansione della settimana è \"{jobs[user_data[0]]}\"")

@bot.message_handler(commands=['start'])
def send_welcome(message):
	if(message.chat.username in users.keys()):
		send_msg(message, 
		   "Ciao benvenuto! \n " +
		   "Questo bot e stato pensato per aiutare i coinquilini che sono ritardati. \n" + 
		   "Gli ideatori del bot @mattsays e @filippoGalliCr sono persone stupide, quindi in caso di errori o bug, attacati al cazzo.\n" +
		   "Bene, da ora in poi ogni lunedi ti manderò il tuo cazzo di turno pezzo di merda. Dopo aver stabilito le regole di base ecco le mie features:", 
		   markup=commands_markup()
		)

	else:
		send_msg(message, "Sei una merda umana, non sei della Aselli Crew! VATTENE!")


@bot.message_handler(regexp=TEXTS['JOB_TEXT'])
def send_job(message):
	if(message.chat.username in users.keys()):
		send_msg(message, f"Ecco il tuo turno bestia:\n{getWeekJob(users[message.chat.username][0])}\nOra vedi di muoverti che non fai mai un cazzo.")
	else:
		bot.send_message(message.chat.id, "Sei una merda umana, vai via bastardo!")
		
@bot.message_handler(regexp=TEXTS['JOBS_TEXT'])
def send_jobs_week(message):
	if(message.chat.username not in users.keys()):
	               	send_msg(message, f"Muori..")
	               	return
	send_msg(message, "Ecco i cazzi degli altri\n")
	jobs = getWeekJobs()
	jobs_str = ''
	for job in jobs.items():
		jobs_str += f"{job[0]}: {job[1]}\n"
	send_msg(message, jobs_str, markup=commands_markup())
	send_msg(message, "Ora torna a lavorare che cazzeggi sempre.")

@bot.message_handler(regexp=TEXTS["HELP_TEXT"])
def send_help(message):
	send_welcome(message)

def schedUpdate():
	global run
	schedule.every().monday.at("08:30").do(cleaning_msg) # Time is in UTC format
	while run:
		schedule.run_pending()
		time.sleep(1)

def main():
	global run
	initializeChatIds()
	schedThread = threading.Thread(target=schedUpdate)
	schedThread.start()

	print("Bot started!")
	while True:
		try:
			bot.polling(none_stop=True, timeout=BOT_TIMEOUT, restart_on_change=False)
		except:
			print(f"Server down - errore: \n {sys.exc_info()[0]}")
			print("...restarting...")
		finally:
			run = False
			schedThread.join()
			print("Bye.")
			exit(0)

if __name__ == "__main__":
        main()
