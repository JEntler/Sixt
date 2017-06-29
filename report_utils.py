import os
import csv
import xlrd
import shelve
import itertools
from decimal import *


def extract_plates(file_name):
	plates = []
	book = xlrd.open_workbook(file_name)
	first_sheet = book.sheet_by_index(0)
	for i in range(1, first_sheet.nrows - 2):
		cells = first_sheet.row_slice(rowx=i, start_colx=2, end_colx=3)
		for cell in cells:
			plates.append(cell.value)
	book.release_resources()
	return plates


def extract_dates(file_name):
	dates = []
	book = xlrd.open_workbook(file_name)
	first_sheet = book.sheet_by_index(0)
	for i in range(1, first_sheet.nrows - 2):
		cells = first_sheet.row_slice(rowx=i, start_colx=5, end_colx=6)
		for cell in cells:
			dates.append(xlrd.xldate_as_tuple(cell.value, book.datemode))
	book.release_resources()
	return dates


def extract_volumes(file_name):
	volumes = []
	book = xlrd.open_workbook(file_name)
	first_sheet = book.sheet_by_index(0)
	for i in range(1, first_sheet.nrows - 2):
		cells = first_sheet.row_slice(rowx=i, start_colx=6, end_colx=7)
		for cell in cells:
			volumes.append(cell.value)
	book.release_resources()
	return volumes


def calculate_costs(file_name, price_db, date_file):
	costs = []
	book = xlrd.open_workbook(file_name)
	first_sheet = book.sheet_by_index(0)
	shelfFile = shelve.open(os.path.join(os.getcwd(), 'data', price_db))
	try:
		price = shelfFile[date_file]
	except KeyError:
		print('$:')
		price = float(input())
		shelfFile[date_file] = price
	shelfFile.close()
	for i in range(1, first_sheet.nrows - 2):
		cells = first_sheet.row_slice(rowx=i, start_colx=6, end_colx=7)
		ppg = list(itertools.repeat(str(price)[0:5], i))
		for cell in cells:
			TWOPLACES = Decimal(10) ** -2
			costs.append(Decimal(cell.value * price).quantize(TWOPLACES))
	book.release_resources()
	return costs, ppg


def convert_dates(dates):
	months = [month[1] for month in dates]
	days = [day[2] for day in dates]
	years = [year[0] for year in dates]
	hours = [hour[3] for hour in dates]
	minutes = [minute[4] for minute in dates]
	seconds = [second[5] for second in dates]
	short_date = list(map(lambda a, b, c: str(a) + "/" + str(b) + "/" + str(c), months, days, years))
	time = list(map(lambda a, b, c: str(a) + ":" + str(b) + ":" + str(c), hours, minutes, seconds))
	return short_date, time


def calculate_total_volume(volumes):
	THREEPLACES = Decimal(10) ** -3
	total_volume = (Decimal(sum(volumes)).quantize(THREEPLACES))
	return total_volume


def calculate_total_cost(costs):
	TWOPLACES = Decimal(10) ** -2
	total_cost = (Decimal(sum(costs)).quantize(TWOPLACES))
	return total_cost


def create_daily_report(date_file, ppg, total_volume, total_cost, daily_db):
	date_delivery = date_file.replace("-", "/")
	day_report = [str(date_delivery), str(ppg[0]), str(total_volume), str(total_cost), total_volume, total_cost]
	shelfFile = shelve.open(os.path.join(os.getcwd(), 'data', daily_db))
	shelfFile[date_file] = day_report
	print("Stored kv pair: " + date_file + ", " + str(day_report))
	shelfFile.close


def create_tickets(short_date, time, plates, ppg, volumes, costs):
	zipped = zip(short_date, time, plates, ppg, volumes, costs)
	tickets = list(zipped)
	return tickets


def create_csv(csv_file, tickets, total_volume, total_cost):
	with open(csv_file, 'w', newline='') as f:
		w = csv.writer(f)
		w.writerow(['refuel_date', 'time_of_delivery', 'license_plate_number', 'unit_cost', 'gallons', 'total_cost'])
		for ticket in tickets:
			w.writerow(ticket)
		w.writerow(['', '', '', '', str(total_volume), str(total_cost)])


def report_to_csv(file_name):
	plates = extract_plates(file_name)
	dates = extract_dates(file_name)
	volumes = extract_volumes(file_name)

	costs = calculate_costs(file_name, price_db, date_file)[0]
	ppg = calculate_costs(file_name, price_db, date_file)[1]

	total_volume = calculate_total_volume(volumes)
	total_cost = calculate_total_cost(costs)

	create_daily_report(date_file, ppg, total_volume, total_cost, daily_db)

	short_date, time = convert_dates(dates)
	tickets = create_tickets(short_date, time, plates, ppg, volumes, costs)
	create_csv(csv_file, tickets, total_volume, total_cost)
