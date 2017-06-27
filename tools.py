#! python3
# tools.py

import os
import re
import csv
import xlwt
import xlrd
import shelve
import smtplib
import requests
import mimetypes
import itertools
from decimal import *
from email import encoders
from bs4 import BeautifulSoup
from email.message import Message
from collections import defaultdict
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def login_to_tcs(s):
	payload = {'sUsrNam': 'rebecca', 'sUsrPwd': 'joule'}
	login_url = 'https://www.myhubmanager.com/login'
	s.post(login_url, data = payload)

def download_tcs_report(s, truck_code, customer_code, date_file, file_name):
	login_to_tcs(s)
	payload = {
		'iRptIdx': '1',
		'iRptOut': '2',
		'sLocCod': '',
		'sTrkCod': truck_code,
		'sFl2Cod': customer_code,
		'dTimStr': date_file,
		'dTimEnd': date_file
		}
	download_url = 'https://www.myhubmanager.com/reports'
	excel = s.post(download_url, data = payload)
	with open(file_name, 'wb') as file:
		file.write(excel.content)

def extract_plates(file_name):
	plates = []
	book = xlrd.open_workbook(file_name)
	first_sheet = book.sheet_by_index(0)
	for i in range(1, first_sheet.nrows-2):
		cells = first_sheet.row_slice(rowx = i, start_colx = 2, end_colx = 3)
		for cell in cells:
			plates.append(cell.value)
	book.release_resources()
	return plates

def extract_dates(file_name):
	dates = []
	book = xlrd.open_workbook(file_name)
	first_sheet = book.sheet_by_index(0)
	for i in range(1, first_sheet.nrows-2):
		cells = first_sheet.row_slice(rowx = i, start_colx = 5, end_colx = 6)
		for cell in cells:
			dates.append(xlrd.xldate_as_tuple(cell.value,book.datemode))
	book.release_resources()
	return dates

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

def extract_volumes(file_name):
	volumes = []
	book = xlrd.open_workbook(file_name)
	first_sheet = book.sheet_by_index(0)
	for i in range(1, first_sheet.nrows-2):
		cells = first_sheet.row_slice(rowx = i, start_colx = 6, end_colx = 7)
		for cell in cells:
			volumes.append(cell.value)
	book.release_resources()
	return volumes

def calculate_total_volume(volumes):
	THREEPLACES = Decimal(10) ** -3
	total_volume = (Decimal(sum(volumes)).quantize(THREEPLACES))
	return total_volume

def calculate_costs(file_name, price_db, date_file):
	costs = []
	book = xlrd.open_workbook(file_name)
	first_sheet = book.sheet_by_index(0)
	shelfFile = shelve.open(os.path.join(os.getcwd(), 'data', price_db))
	try:
		price = shelfFile[date_file]
	except KeyError:
		print ('$:')
		price = float(input())
		shelfFile[date_file] = price
	shelfFile.close()
	for i in range(1, first_sheet.nrows-2):
		cells = first_sheet.row_slice(rowx = i, start_colx = 6, end_colx = 7)
		ppg = list(itertools.repeat(str(price)[0:5],i))
		for cell in cells:
			TWOPLACES = Decimal(10) ** -2
			costs.append(Decimal(cell.value*price).quantize(TWOPLACES))
	book.release_resources()
	return costs, ppg

def calculate_total_cost(costs):
	TWOPLACES = Decimal(10) ** -2
	total_cost = (Decimal(sum(costs)).quantize(TWOPLACES))
	return total_cost

def create_daily_report(date_file, ppg, total_volume, total_cost, daily_db):
	date_delivery = date_file.replace("-","/")
	day_report = [str(date_delivery),str(ppg[0]),str(total_volume),str(total_cost),total_volume,total_cost]
	shelfFile = shelve.open(os.path.join(os.getcwd(), 'data', daily_db))
	shelfFile[date_file] = day_report
	print("Stored kv pair: " + date_file + ", " + str(day_report))
	shelfFile.close

def create_tickets(short_date, time, plates, ppg, volumes, costs):
	zipped = zip(short_date, time, plates, ppg, volumes, costs)
	tickets = list(zipped)
	return tickets

def create_csv(csv_file, tickets, total_volume, total_cost):
	with open(csv_file,'w',newline='') as f:
		w = csv.writer(f)
		w.writerow(['refuel_date', 'time_of_delivery', 'license_plate_number', 'unit_cost', 'gallons', 'total_cost'])
		for ticket in tickets:
			w.writerow(ticket)
		w.writerow(['','','','', str(total_volume), str(total_cost)])

def email_csv(send_to, send_to_cc, send_to_bcc, csv_file):
	emailfrom = 'joe.entler@joulerefuel.com'
	emailto = send_to
	emailtoCc = send_to_cc
	emailtoBcc = send_to_bcc
	fileToSend = csv_file
	username = 'joe.entler@joulerefuel.com'
	password = 'joulerefuel'

	msg = MIMEMultipart()
	msg["From"] = emailfrom
	msg["To"] = ", ".join(emailto)
	msg["Cc"] = ", ".join(emailtoCc)
	msg["Subject"] = csv_file
	msg.preamble = ''

	ctype, encoding = mimetypes.guess_type(fileToSend)
	if ctype is None or encoding is not None:
		ctype = "application/octet-stream"

	maintype, subtype = ctype.split("/", 1)

	if maintype == "text":
		fp = open(fileToSend)
		# Note: we should handle calculating the charset
		attachment = MIMEText(fp.read(), _subtype=subtype)
		fp.close()
	elif maintype == "image":
		fp = open(fileToSend, "rb")
		attachment = MIMEImage(fp.read(), _subtype=subtype)
		fp.close()
	elif maintype == "audio":
		fp = open(fileToSend, "rb")
		attachment = MIMEAudio(fp.read(), _subtype=subtype)
		fp.close()
	else:
		fp = open(fileToSend, "rb")
		attachment = MIMEBase(maintype, subtype)
		attachment.set_payload(fp.read())
		fp.close()
		encoders.encode_base64(attachment)
	attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
	msg.attach(attachment)

	server = smtplib.SMTP("smtp.gmail.com:587")
	server.starttls()
	server.login(username,password)
	server.sendmail(emailfrom, emailto+emailtoBcc, msg.as_string())
	server.quit()

def email_price(send_to, send_to_cc, send_to_bcc, date_file, ppg):
	emailfrom = 'joe.entler@joulerefuel.com'
	emailto = send_to
	emailtoCc = send_to_cc
	emailtoBcc = send_to_bcc
	username = 'joe.entler@joulerefuel.com'
	password = 'joulerefuel'

	msg = MIMEMultipart()
	msg["From"] = emailfrom
	msg["To"] = ", ".join(emailto)
	msg["Cc"] = ", ".join(emailtoCc)
	msg["Subject"] = date_file + ' Midgrade Price: $' + ppg[0]
	msg.preamble = ''

	server = smtplib.SMTP("smtp.gmail.com:587")
	server.starttls()
	server.login(username,password)
	server.sendmail(emailfrom, emailto+emailtoBcc, msg.as_string())
	server.quit()

def sixt_daily(s, date_file, truck):
	send_to = ['kirill.bryzgov@sixt.com'] #['kirill.bryzgov@sixt.com']
	send_to_cc = []
	send_to_bcc = ['rebecca.suissa@joulerefuel.com'] #['rebecca.suissa@joulerefuel.com']
	file_name = 'black_truck.xls'
	file_name2 = 'white_truck_000.xls'
	price_db = 'opisData'
	daily_db = 'daily'
	csv_file = 'Refuel Schedule ' + date_file + '.csv'
	if truck == 'white':
		download_tcs_report(s, '49178A2', 'sixt', date_file, file_name2)

		plates = extract_plates(file_name2)
		dates = extract_dates(file_name2)
		volumes = extract_volumes(file_name2)

		costs = calculate_costs(file_name2, price_db, date_file)[0]
		ppg = calculate_costs(file_name2, price_db, date_file)[1]

		total_volume = calculate_total_volume(volumes)
		total_cost = calculate_total_cost(costs)

		create_daily_report(date_file, ppg, total_volume, total_cost, daily_db)

		short_date, time = convert_dates(dates)
		tickets = create_tickets(short_date, time, plates, ppg, volumes, costs)
		create_csv(csv_file, tickets, total_volume, total_cost)
		email_csv(send_to, send_to_cc, send_to_bcc, csv_file)
	elif truck == 'black':
		download_tcs_report(s, '71224W1', '', date_file, file_name)

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
		email_csv(send_to, send_to_cc, send_to_bcc, csv_file)
	elif truck == 'both': # list.extend()
		download_tcs_report(s, '71224W1', '', date_file, file_name)
		download_tcs_report(s, '49178A2', 'sixt', date_file, file_name2)

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

def silvercar_daily(s, date_file, truck):
	send_to = ['dante.giles@silvercar.com'] #['dante.giles@silvercar.com']
	send_to_cc = ['celese.cooper@silvercar.com'] #['celese.cooper@silvercar.com']
	send_to_bcc = ['rebecca.suissa@joulerefuel.com'] #['rebecca.suissa@joulerefuel.com']
	file_name = 'white_truck_111.xls'
	price_db = 'opisMidgrade'
	daily_db = 'dailysilvercar'
	if truck == 'white':
		download_tcs_report(s, '49178A2', 'silvercar', date_file, file_name)

		volumes = extract_volumes(file_name)
		total_volume = calculate_total_volume(volumes)

		costs, ppg = calculate_costs(file_name, price_db, date_file)
		total_cost = calculate_total_cost(costs)

		create_daily_report(date_file, ppg, total_volume, total_cost, daily_db)
		email_price(send_to, send_to_cc, send_to_bcc, date_file, ppg)
	elif truck == 'zero':
		volumes = extract_volumes('zero.xls')
		total_volume = calculate_total_volume(volumes)

		costs, ppg = calculate_costs('zero.xls', price_db, date_file)
		total_cost = calculate_total_cost(costs)

		create_daily_report(date_file, ppg, total_volume, total_cost, daily_db)
		email_price(send_to, send_to_cc, send_to_bcc, date_file, ppg)
