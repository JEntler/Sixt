import os
import csv
import xlrd
import pdfkit
import shelve
import itertools
import datetime as DT
from decimal import *
from jinja2 import Environment, FileSystemLoader


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


def define_data(invoice_db, daily_db, billing_period):
	days_late = int(input('Days Late: '))
	this_invoice_date = DT.date.today() - DT.timedelta(days=days_late)
	last_invoice_date = str(this_invoice_date - DT.timedelta(days=billing_period))
	shelfFile = shelve.open(os.path.join(os.getcwd(), 'data', invoice_db))
	try:
		invoice_num = int(shelfFile[last_invoice_date]) + 1
	except KeyError:
		invoice_num = int(input('#: '))
	shelfFile[str(this_invoice_date)] = invoice_num
	shelfFile.close
	days = []
	volumes = []
	costs = []
	shelfFile = shelve.open(os.path.join(os.getcwd(), 'data', daily_db))
	for i in range(billing_period, 0, -1):
		a_day = shelfFile[str(this_invoice_date - DT.timedelta(days=i))]
		days.append(a_day)
		volumes.append(a_day[4])
		costs.append(a_day[5])
	shelfFile.close
	total_volume = sum(volumes)
	total_cost = sum(costs)
	payment_due = str(this_invoice_date + DT.timedelta(days=4))
	return invoice_num, days, total_volume, total_cost, payment_due


def render_html(invoice_db, daily_db, report_html, render_name, billing_period):
	invoice_num, days, total_volume, total_cost, payment_due = define_data(invoice_db, daily_db, billing_period)
	env = Environment(loader=FileSystemLoader('templates'))
	template = env.get_template(report_html)
	f = open(os.path.join(os.getcwd(), 'records', render_name), 'w')
	f.write(template.render(
		invoice_num=invoice_num,
		payment_due=payment_due,
		days=days,
		total_volume='{0:,}'.format(total_volume),
		total_cost='{0:,}'.format(total_cost)
	))
	f.close()
	return invoice_num


def make_pdf(render_name, pdf_name):
	options = {}
	path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
	config = pdfkit.configuration(wkhtmltopdf=bytes(path_wkthmltopdf, 'utf-8'))
	pdfkit.from_file(os.path.join(os.getcwd(), 'records', render_name), pdf_name, options=options, configuration=config)
