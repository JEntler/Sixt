import smtplib
import mimetypes
import credentials
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


def email_csv(send_to, send_to_cc, send_to_bcc, csv_file):
	emailfrom = credentials.GMAIL_USER
	emailto = send_to
	emailtoCc = send_to_cc
	emailtoBcc = send_to_bcc
	fileToSend = csv_file
	username = credentials.GMAIL_USER
	password = credentials.GMAIL_PASS

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
	server.login(username, password)
	server.sendmail(emailfrom, emailto + emailtoBcc, msg.as_string())
	server.quit()


def email_price(send_to, send_to_cc, send_to_bcc, date_file, grade, ppg):
	emailfrom = credentials.GMAIL_USER
	emailto = send_to
	emailtoCc = send_to_cc
	emailtoBcc = send_to_bcc
	username = credentials.GMAIL_USER
	password = credentials.GMAIL_PASS

	msg = MIMEMultipart()
	msg["From"] = emailfrom
	msg["To"] = ", ".join(emailto)
	msg["Cc"] = ", ".join(emailtoCc)
	msg["Subject"] = date_file + ' {} Price: $'.format(grade) + ppg[0]
	msg.preamble = ''

	server = smtplib.SMTP("smtp.gmail.com:587")
	server.starttls()
	server.login(username, password)
	server.sendmail(emailfrom, emailto + emailtoBcc, msg.as_string())
	server.quit()


def email_pdf(pdf_name, emailto, emailtoCc, emailtoBcc):
	emailfrom = credentials.GMAIL_USER
	fileToSend = pdf_name
	username = credentials.GMAIL_USER
	password = credentials.GMAIL_PASS

	msg = MIMEMultipart()
	msg["From"] = emailfrom
	msg["To"] = ", ".join(emailto)
	msg["Cc"] = ", ".join(emailtoCc)
	msg["Subject"] = "81012272 {}".format(credentials.SIXT_NAME)
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
	server.login(username, password)
	server.sendmail(emailfrom, emailto + emailtoBcc, msg.as_string())
	server.quit()
