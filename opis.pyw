#! python3
# opis.pyw

import os
import time
import shelve
import requests
from bs4 import BeautifulSoup

def opis_authenticate(customer_token, s):
	payload = {'CustomerToken': customer_token}
	authenticate_url = 'http://services.opisnet.com/RealtimePriceService/RealtimePriceServicePlus.asmx/Authenticate'
	r = s.post(authenticate_url, data = payload)
	soup = BeautifulSoup(r.text, 'xml')
	user_ticket = soup.string
	return user_ticket
	
def opis_getzipcoderesults(customer_token, s, zip):
	user_ticket = opis_authenticate(customer_token, s)
	payload = {'UserTicket': user_ticket, 'ZipCode': zip}
	getzipcoderesults_url = 'http://services.opisnet.com/RealtimePriceService/RealtimePriceServicePlus.asmx/GetZipCodeResults'
	r = s.post(getzipcoderesults_url, data = payload)
	soup = BeautifulSoup(r.text, 'xml')
	return soup

customer_token = 'zfb8o9+FMN4FUIgEdrgbYQ=='
s = requests.session()
zip = 90045

soup = opis_getzipcoderesults(customer_token, s, zip)
unleaded_prices = [float(i.text.strip()) for i in soup.select('Unleaded_Price')]
midgrade_prices = [float(i.text.strip()) for i in soup.select('MidGrade_Price')]

date_key = time.strftime('%Y-%m-%d')

opisData = shelve.open(os.path.join(os.getcwd(), 'data', 'opisData'))
unleaded_avg = (sum(unleaded_prices)/len(unleaded_prices)) + .60
opisData[date_key] = unleaded_avg
opisData.close()

opisMidgrade = shelve.open(os.path.join(os.getcwd(), 'data', 'opisMidgrade'))
midgrade_avg = (sum(midgrade_prices)/len(midgrade_prices)) + .60
opisMidgrade[date_key] = midgrade_avg
opisMidgrade.close()

gm = shelve.open(os.path.join(os.getcwd(), 'data', 'gm'))
gm_unleaded = float(soup.find(text='G & M OIL #194').findNext('Unleaded_Price').contents[0])
gm[date_key] = gm_unleaded
gm.close()

gmmidgrade = shelve.open(os.path.join(os.getcwd(), 'data', 'gmmidgrade'))
gm_midgrade = float(soup.find(text='G & M OIL #194').findNext('MidGrade_Price').contents[0])
gmmidgrade[date_key] = gm_midgrade
gmmidgrade.close()