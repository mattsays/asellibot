from datetime import date, datetime
from dateutil import rrule

class Jobs:
	def __init__(self, json):
		self.json = json
		self.start_date = datetime.strptime(json["bigbang"], "%d/%m/%Y").date()
		self.jobs = self.json["jobs"]
		self.members_num = len(self.json["members"].keys())

	def getWeekIndex(self):
		weeks = rrule.rrule(rrule.WEEKLY, dtstart=self.start_date, until=date.today())
		return (weeks.count() - 1) % len(self.jobs)

	def getWeekJobs(self):
		week_index = self.getWeekIndex()
		jobs = {}
		for username in self.json["members"].keys():
			display_name = self.json["members"][username]["display_name"]
			bigbang_index = self.json["members"][username]["bigbang_index"]
			jobs[display_name] = self.jobs[(bigbang_index + week_index) % self.members_num]
		return jobs

	def getWeekJob(self, username):
		week_index = self.getWeekIndex()
		bigbang_index = self.json["members"][username]["bigbang_index"]
		return self.jobs[(bigbang_index + week_index) % self.members_num]
