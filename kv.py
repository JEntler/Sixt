#! python3
# kv.py

import os
import sys
import shelve
from tools import day_add

def kv(option):
	print("----------" + option + "----------")
	shelfFile = shelve.open(os.path.join(os.getcwd(), 'data', option))
	klist = list(shelfFile.keys())
	print ("Keys: " + str(sorted(klist)))
	print ("Key:")
	key = str(input())

	if key == 'all':
		for k,v in sorted(shelfFile.items()):
			print(k,v)
		return

	try:
		value = shelfFile[key]
		print("Value: " + str(value))
		print("Would you like to change the key's value?")
		print("y/n/d?")

		resp = str(input())
		if resp == 'y':
			if option in ['daily', 'dailysilvercar', 'sixttransition']:
				shelfFile.close()
				day_add(option)
			else:
				print("Enter a new value:")
				if option in ['opisData', 'opisMidgrade', 'gm', 'gmmidgrade']:
					new_value = float(input())
				else:
					new_value = input()
				shelfFile[key] = new_value
				print("Stored kv pair: " + key + ", " + str(new_value))

		elif resp.lower() == 'n':
			sys.exit

		elif resp.lower() == 'd':
			print("Are you sure you wish to delete stored kv pair: " + key + ", " + str(value) + " ?")
			print("y/n?")
			resp2 = str(input())
			if resp2.lower() == 'y': 
				del shelfFile[key]
				print ("kv pair deleted")
			elif resp2.lower() == 'n':
				sys.exit

	except KeyError:
		if option in ['daily', 'dailysilvercar', 'sixttransition']:
			shelfFile.close()
			day_add(option)
		else:
			print("Enter a new value:")
			if option in ['opisData', 'opisMidgrade', 'gm', 'gmmidgrade']:
				new_value = float(input())
			else:
				new_value = input()
			shelfFile[key] = new_value
			print("Stored kv pair: " + key + ", " + str(new_value))
	shelfFile.close()

print ("Which kv would you like to see?")
print ("-------------------------------")
print ("1. INVOICE")
print ("2. OPIS DATA")
print ("3. DAILY")
print ("4. GM")
print ("5. OPIS MIDGRADE")
print ("6. GM MIDGRADE")
print ("7. DAILY SILVERCAR")
print ("8. INVOICE SILVERCAR")
print ("9. SIXT TRANSITION")
print ("10. SIXT TRANSITION INVOICE")
print ("-------------------------------")
print ("1/2/3/4/5/6/7/8/9/10?")

choice = input()
if choice == '1':
	kv('invoice')
elif choice == '2':
	kv('opisData')
elif choice == '3':
	kv('daily')
elif choice == '4':
	kv('gm')
elif choice == '5':
	kv('opisMidgrade')
elif choice == '6':
	kv('gmmidgrade')
elif choice == '7':
	kv('dailysilvercar')
elif choice == '8':
	kv('invoicesilvercar')
elif choice == '9':
	kv('sixttransition')
elif choice == '10':
	kv('invoicesixttransition')