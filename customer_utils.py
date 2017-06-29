import credentials
from tcs_utils import download_tcs_report
from report_utils import extract_dates, extract_plates, extract_volumes, report_to_csv, calculate_costs, convert_dates, calculate_total_volume, calculate_total_cost, create_daily_report, create_tickets, create_csv
from email_utils import email_csv, email_price


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

	if truck == 'white':
		file_name = 'white_truck_000.xls'
		report_to_csv(file_name)
		email_csv(send_to, send_to_cc, send_to_bcc, csv_file)
	elif truck == 'black':
		file_name = 'black_truck.xls'
		report_to_csv(file_name)
		email_csv(send_to, send_to_cc, send_to_bcc, csv_file)
	elif truck == 'both':  # list.extend()
		file_name = 'black_truck.xls'
		file_name2 = 'white_truck_000.xls'

		plates = extract_plates(file_name) + extract_plates(file_name2)
		dates = extract_dates(file_name) + extract_dates(file_name2)
		volumes = extract_volumes(file_name) + extract_volumes(file_name2)

		costs = calculate_costs(file_name, price_db, date_file)[0] + calculate_costs(file_name2, price_db, date_file)[0]
		ppg = calculate_costs(file_name, price_db, date_file)[1] + calculate_costs(file_name2, price_db, date_file)[1]

		total_volume = calculate_total_volume(volumes)
		total_cost = calculate_total_cost(costs)

		create_daily_report(date_file, ppg, total_volume, total_cost, daily_db)

		short_date, time = convert_dates(dates)
		tickets = create_tickets(short_date, time, plates, ppg, volumes, costs)
		create_csv(csv_file, tickets, total_volume, total_cost)
		email_csv(send_to, send_to_cc, send_to_bcc, csv_file)
	elif truck == 'zero':
		volumes = extract_volumes('zero.xls')
		total_volume = calculate_total_volume(volumes)

		costs, ppg = calculate_costs('zero.xls', price_db, date_file)
		total_cost = calculate_total_cost(costs)

		create_daily_report(date_file, ppg, total_volume, total_cost, daily_db)


def silvercar_daily(s, date_file, truck, test):
	if test is False:
		send_to = credentials.SILVERCAR_TO
		send_to_cc = credentials.SILVERCAR_CC
		send_to_bcc = credentials.SILVERCAR_BCC
	else:
		send_to = send_to_cc = send_to_bcc = credentials.TEST_USER
	file_name = 'white_truck_111.xls'
	price_db = 'opisMidgrade'
	daily_db = 'dailysilvercar'
	grade = "Midgrade"
	if truck == 'white':
		download_tcs_report(s, '49178A2', 'silvercar', date_file, file_name)

		volumes = extract_volumes(file_name)
		total_volume = calculate_total_volume(volumes)

		costs, ppg = calculate_costs(file_name, price_db, date_file)
		total_cost = calculate_total_cost(costs)

		create_daily_report(date_file, ppg, total_volume, total_cost, daily_db)
		email_price(send_to, send_to_cc, send_to_bcc, date_file, grade, ppg)
	elif truck == 'zero':
		volumes = extract_volumes('zero.xls')
		total_volume = calculate_total_volume(volumes)

		costs, ppg = calculate_costs('zero.xls', price_db, date_file)
		total_cost = calculate_total_cost(costs)

		create_daily_report(date_file, ppg, total_volume, total_cost, daily_db)
		email_price(send_to, send_to_cc, send_to_bcc, date_file, grade, ppg)
