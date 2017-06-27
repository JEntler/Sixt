from tools import *

s = ''

def sixt_daily(s, date_file, file_name):
	price_db = 'opisData'
	daily_db = 'sixttransition'

	volumes = extract_volumes(file_name)
	total_volume = calculate_total_volume(volumes)

	costs, ppg = calculate_costs(file_name, price_db, date_file)
	total_cost = calculate_total_cost(costs)

	create_daily_report(date_file, ppg, total_volume, total_cost, daily_db)

#for i in range (12, 26):
#	date_file = '2016-12-' + str(i)
#	file_name = str(i) + 'sixt.xls'
#	sixt_daily(s, date_file, file_name)

def silvercar_daily(s, date_file, file_name):
	price_db = 'opisMidgrade'
	daily_db = 'dailysilvercar'

	volumes = extract_volumes(file_name)
	total_volume = calculate_total_volume(volumes)

	costs, ppg = calculate_costs(file_name, price_db, date_file)
	total_cost = calculate_total_cost(costs)

	create_daily_report(date_file, ppg, total_volume, total_cost, daily_db)

#for i in range (12, 26):
#	date_file = '2016-12-' + str(i)
#	file_name = str(i) + 'silvercar.xls'
#	silvercar_daily(s, date_file, file_name)