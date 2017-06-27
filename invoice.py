#! python3
# invoice.py

import os
import shelve
import pdfkit
import smtplib
import mimetypes
import datetime as DT
from email import encoders
from email.message import Message
from collections import defaultdict
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
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
	payment_due=str(this_invoice_date + DT.timedelta(days=4))
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
	options={}
	path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
	config = pdfkit.configuration(wkhtmltopdf=bytes(path_wkthmltopdf, 'utf-8'))
	pdfkit.from_file(os.path.join(os.getcwd(), 'records', render_name), pdf_name, options=options, configuration=config)

def email_pdf(pdf_name, emailto, emailtoCc, emailtoBcc):
	emailfrom = 'joe.entler@joulerefuel.com'
	fileToSend = pdf_name
	username = 'joe.entler@joulerefuel.com'
	password = 'joulerefuel'

	msg = MIMEMultipart()
	msg["From"] = emailfrom
	msg["To"] = ", ".join(emailto)
	msg["Cc"] = ", ".join(emailtoCc)
	msg["Subject"] = str(pdf_name)[:-4]
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

def sixt_invoice():
	invoice_db = 'invoice'
	daily_db = 'daily'
	report_html = 'report_sixt.html'
	render_name = 'render_sixt.html'
	billing_period = 7

	emailto = ['accountspayable-us@sixt.com'] #['accountspayable-us@sixt.com']
	emailtoCc = ['kirill.bryzgov@sixt.com'] #['kirill.bryzgov@sixt.com']
	emailtoBcc = ['rebecca.suissa@joulerefuel.com','bernard.suissa@joulerefuel.com'] #['rebecca.suissa@joulerefuel.com','bernard.suissa@joulerefuel.com']

	invoice_num = render_html(invoice_db, daily_db, report_html, render_name, billing_period)
	pdf_name = str("Sixt_Invoice #" + str(invoice_num) + " Kirill Bryzgov" + ".pdf")
	make_pdf(render_name, pdf_name)
	email_pdf(pdf_name, emailto, emailtoCc, emailtoBcc)

def silvercar_invoice():
	invoice_db = 'invoicesilvercar'
	daily_db = 'dailysilvercar'
	report_html = 'report_silvercar.html'
	render_name = 'render_silvercar.html'
	billing_period = 31 # 31

	invoice_num = render_html(invoice_db, daily_db, report_html, render_name, billing_period)
	pdf_name = str("Silvercar_Invoice #" + str(invoice_num) + ".pdf")
	make_pdf(render_name, pdf_name)

	pages_to_keep = [0]
	from PyPDF2 import PdfFileWriter, PdfFileReader
	infile = PdfFileReader(pdf_name, 'rb')
	output = PdfFileWriter()

	for i in range(infile.getNumPages()):
		p = infile.getPage(i)
		if i in pages_to_keep:
			output.addPage(p)

	with open('newfile.pdf', 'wb') as f:
		output.write(f)

if __name__ == '__main__':
	sixt_invoice()
	#silvercar_invoice()