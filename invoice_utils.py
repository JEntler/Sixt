import os
import pdfkit
import shelve
import datetime as DT
from jinja2 import Environment, FileSystemLoader


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
