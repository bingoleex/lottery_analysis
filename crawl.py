import json
from datetime import date, timedelta
import datetime
import time
from selenium import webdriver
import sqlite3
import json
import logging

def crawl(start, end, cursor, api_url):

	delta = end - start
	json_file = open('data2.json', 'a')
	json_file.write('[')

	driver = webdriver.Chrome()

	for i in range(delta.days + 1):
		current_craw_date = start + timedelta(days=i)
		request_url = api_url.format(str(current_craw_date))
		logging.info('Current crawl:', request_url)
		driver.get(request_url)

		data = json.loads(driver.find_element_by_xpath('/html/body').text)
		for item in data['result']['data']:
			columns = str(','.join(item.keys())).upper()
			values = ':'+', :'.join(item.keys())

			if i == 0:
				del_sql = "DELETE FROM RESULT WHERE PREDRAWTIME LIKE '%{0}%'".format(start)
				cursor.execute(del_sql)

			exe_sql = 'INSERT INTO RESULT ({0}) VALUES ({1})'.format(columns, values)
			cursor.execute(exe_sql, item)

	driver.close()

	logging.info('done')


def update_the_database():
	try:
		with sqlite3.connect('result.db') as conn:
			cursor = conn.cursor()
			exe_sql = 'SELECT PARAM_VALUE FROM SETTINGS WHERE PARAM="LAST_UPDATED"'
			logging.info("sql:", exe_sql)
			cursor.execute(exe_sql)
			last_updated = cursor.fetchone()[0]

			exe_sql = 'SELECT PARAM_VALUE FROM SETTINGS WHERE PARAM="API_URL"'
			logging.info("sql:", exe_sql)
			cursor.execute(exe_sql)
			api_url = cursor.fetchone()[0]

			crawl(datetime.datetime.strptime(last_updated, '%Y-%m-%d').date(), datetime.datetime.now().date(), cursor, api_url)

			exe_sql = "UPDATE SETTINGS SET PARAM_VALUE = '{0}' WHERE PARAM=\"LAST_UPDATED\" ".format(datetime.datetime.now().strftime('%Y-%m-%d'))
			logging.info("sql:", exe_sql)
			print("sql:", exe_sql)
			cursor.execute(exe_sql)

			conn.commit()

		return True
	except Exception as e:
		logging.info(e)
		print(e)
		return False

if __name__ == '__main__':
	update_the_database()
