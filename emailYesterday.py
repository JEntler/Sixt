#! python3
# emailYesterday.py

try:
	import opis
except ZeroDivisionError:
	print("OPIS Failure")

import requests
from customer_utils import sixt_daily, silvercar_daily
import datetime as DT

if __name__ == '__main__':
	date_file = str(DT.date.today() - DT.timedelta(days=1))
else:
	date_file = str(input('YYYY/MM/DD: ')).replace("/", "-")

s = requests.session()

test = False
sixt_daily(s, date_file, truck='both', test=test)
silvercar_daily(s, date_file, truck='white', test=test)
