#! python3
# emailYesterday.pyw

import opis
from tools import *
import datetime as DT

if __name__ == '__main__':
	date_file = str(DT.date.today() - DT.timedelta(days=1))
else:
	date_file = str(input('YYYY/MM/DD: ')).replace("/","-")

s = requests.session()
sixt_daily(s, date_file, truck='both')
silvercar_daily(s, date_file, truck='white')