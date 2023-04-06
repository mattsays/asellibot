import telebot
import schedule
import time
import threading
from datetime import date, datetime
from dateutil import rrule


# Constants

START_DATE = datetime.strptime("10/10/2022", "%d/%m/%Y").date()
# Base jobs for start date: 
# Filippo : Bagno (0)
# Mattia : Pavimenti (1)
# Michele : Cucina (2)
FIRST_INDICES = {'Filippo': 0, 'Mattia': 1, 'Michele': 2}
JOB_TYPES = ["Bagno 🚽", "Pavimenti 🧹", "Piano cottura e Bidoni 🔥/🗑️"]

run = True

# Weekly calculated jobs 

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

# Telegram related part

users = {
	"mattsays": ["Mattia"],
	"filippoGalliCr": ["Filippo"],
	"Michelepave": ["Michele"]
}

bot = telebot.TeleBot("6247355614:AAHh0K4EK7SffTX2-Gu-rhiN0pYke_Wm_R4", parse_mode=False)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	if(message.chat.username in users.keys()):
		bot.send_message(message.chat.id, "Bella comparema")
		if len(users[message.chat.username]) == 1:
			users[message.chat.username].append(message.chat.id)
		cleaningMsg()
	else:
		bot.send_message(message.chat.id, "Sei una merda umana!")

@bot.message_handler(commands=['mansione'])
def send_job(message):
	if(message.chat.username in users.keys()):
		if len(users[message.chat.username]) == 1:
			users[message.chat.username].append(message.chat.id)
		bot.send_message(users[message.chat.username][1], getWeekJob(users[message.chat.username][0]))

def cleaningMsg():
	jobs = getWeekJobs()
	for user_data in users.values():
		if(len(user_data) != 2):
			continue
		bot.send_message(user_data[1], f"Bungiorno la tua mansione della settimana è \"{jobs[user_data[0]]}\"")

def schedUpdate():
	global run
	schedule.every().monday.at("10:30").do(cleaningMsg)
	while run:
		schedule.run_pending()
		time.sleep(1)

schedThread = threading.Thread(target=schedUpdate)
schedThread.start()

print("Bot started!")
bot.infinity_polling()
