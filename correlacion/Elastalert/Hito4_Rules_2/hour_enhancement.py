import dateutil.parser

from elastalert.enhancements import BaseEnhancement
from elastalert.enhancements import DropMatchException

class HourRangeEnhancement(BaseEnhancement):
	def process(self, match):
		timestamp = dateutil.parser.parse(match['timestamp']).time()
                # UTC time (Madrid ==> UTC + 1)
		time_start = dateutil.parser.parse("9:00").time()
        time_end = dateutil.parser.parse("12:00").time()
		if timestamp > time_start or timestamp < time_end:
			raise DropMatchException()