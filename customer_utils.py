import credentials
from tcs_utils import download_tcs_report
from email_utils import email_csv, email_price
from report_utils import reports_to_csv, reports_to_db


def sixt_daily(s, date_file, truck, test):
	if test is False:
		send_to = credentials.SIXT_TO
		send_to_cc = credentials.SIXT_CC
		send_to_bcc = credentials.SIXT_BCC
	else:
		send_to = send_to_cc = send_to_bcc = credentials.TEST_USER

	price_db = 'opisData'
	daily_db = 'daily'
	csv_file = 'Refuel Schedule ' + date_file + '.csv'

	download_tcs_report(s, '71224W1', '', date_file, 'black_truck.xls')
	download_tcs_report(s, '49178A2', 'sixt', date_file, 'white_truck_000.xls')

	if truck == 'zero':
		files = ['zero.xls']
		reports_to_db(files, price_db, daily_db, date_file)
		return

	elif truck == 'white':
		files = ['white_truck_000.xls']
	elif truck == 'black':
		files = ['black_truck.xls']
	elif truck == 'both':
		files = ['black_truck.xls', 'white_truck_000.xls']

	reports_to_csv(files, price_db, daily_db, date_file, csv_file)
	email_csv(send_to, send_to_cc, send_to_bcc, csv_file)


def silvercar_daily(s, date_file, truck, test):
	if test is False:
		send_to = credentials.SILVERCAR_TO
		send_to_cc = credentials.SILVERCAR_CC
		send_to_bcc = credentials.SILVERCAR_BCC
	else:
		send_to = send_to_cc = send_to_bcc = credentials.TEST_USER

	price_db = 'opisMidgrade'
	daily_db = 'dailysilvercar'
	grade = "Midgrade"

	download_tcs_report(s, '49178A2', 'silvercar', date_file, 'white_truck_111.xls')

	if truck == 'white':
		files = ['white_truck_111.xls']
	elif truck == 'zero':
		files = ['zero.xls']

	ppg = reports_to_db(files, price_db, daily_db, date_file)
	email_price(send_to, send_to_cc, send_to_bcc, date_file, grade, ppg)
