import constants
import credentials


def login_to_tcs(s):
	payload = {'sUsrNam': credentials.TCS_USER, 'sUsrPwd': credentials.TCS_PASS}
	login_url = constants.TCS_LOGIN_URL
	s.post(login_url, data=payload)


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
	download_url = constants.TCS_REPORT_URL
	excel = s.post(download_url, data=payload)
	with open(file_name, 'wb') as file:
		file.write(excel.content)
