import xlrd


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
