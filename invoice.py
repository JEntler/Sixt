#! python3
# invoice.py

import credentials
from email_utils import email_pdf
from invoice_utils import render_html, make_pdf


def sixt_invoice(test):
	invoice_db = 'invoice'
	daily_db = 'daily'
	report_html = 'report_sixt.html'
	render_name = 'render_sixt.html'
	billing_period = 7

	if test is False:
		emailto = credentials.SIXT_TO_INVOICE
		emailtoCc = credentials.SIXT_CC_INVOICE
		emailtoBcc = credentials.SIXT_BCC_INVOICE
	else:
		emailto = emailtoCc = emailtoBcc = credentials.TEST_USER

	invoice_num = render_html(invoice_db, daily_db, report_html, render_name, billing_period)
	pdf_name = str(
		"Sixt_Invoice #" + str(invoice_num) + " {}".format(credentials.SIXT_NAME) + ".pdf")
	make_pdf(render_name, pdf_name)
	email_pdf(pdf_name, emailto, emailtoCc, emailtoBcc)


def silvercar_invoice():
	invoice_db = 'invoicesilvercar'
	daily_db = 'dailysilvercar'
	report_html = 'report_silvercar.html'
	render_name = 'render_silvercar.html'
	billing_period = 31  # 31

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
	sixt_invoice(test=True)
	# silvercar_invoice()
