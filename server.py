from flask import Flask, jsonify, render_template
from flask_cors import CORS
import sqlite3
from collections import defaultdict
from flask import request
import json
from cal_the_currency import *
from datetime import date, timedelta
import datetime
from crawl import *

app = Flask(__name__)
DATABASE_FILE_NAME = 'result.db'
BY_DATE = 0
BY_PERIOD = 1
BY_VOLUME = 2
GET_PRIZE = 3

CORS(app)

@app.route('/tendency/date/', methods=['POST', 'GET'])
def get_tendency_by_date():
	try:
		day = request.args['date']
		result = get_result(BY_DATE, day)
		step_result = get_bet_process_detail([list(map(int, x['bbet_code'].split(','))) for x in result])
	except:
		result = []
		current_date = datetime.datetime.now().strftime('%Y-%m-%d')
		return render_template('tendency_by_date.html', result_set=[], other_result=[], total_los=[], total_win=[],current_date=current_date)

	if step_result == []:
		return render_template('tendency_by_date.html', result_set=[], other_result=[], total_los=[], total_win=[],current_date=day)

	return render_template('tendency_by_date.html', 
		result_set = result, 
		other_result = step_result['step_detail'],
		total_win = step_result['total_win'],
		total_los = step_result['total_los'],
		current_date=day)

@app.route('/tendency/period/', methods=['POST', 'GET'])
def get_tendency_by_peroid():
	try:
		start = request.args['start_date']
		end = end_date_plus(request.args['end_date'])
		result = get_result(BY_PERIOD, [start, end])
		step_result = get_bet_process_detail([list(map(int, x['bbet_code'].split(','))) for x in result])
	except:
		result = []
		current_date = datetime.datetime.now().strftime('%Y-%m-%d')
		return render_template('tendency_by_period.html', 
			result_set=[], 
			other_result=[], 
			total_los=[], 
			total_win=[],
			start=current_date,
			end=current_date)

	if step_result == []:
		return render_template('tendency_by_period.html', 
			result_set=[], 
			other_result=[], 
			total_los=[], 
			total_win=[],
			start=start,
			end=request.args['end_date'])

	return render_template('tendency_by_period.html', 
		result_set = result, 
		other_result = step_result['step_detail'],
		total_win = step_result['total_win'],
		total_los = step_result['total_los'],
		start=start,
		end=request.args['end_date'])

@app.route('/tendency/volume/', methods=['POST', 'GET'])
def get_tendency_by_volume():
	try:
		print('ok')
		start = request.args['start']
		end = request.args['end']
		result = get_result(BY_VOLUME, [int(start), int(end)])
		step_result = get_bet_process_detail([list(map(int, x['bbet_code'].split(','))) for x in result])	
	except:
		result = []
		return render_template('tendency_by_volume.html', 
			result_set=[], 
			other_result=[], 
			total_los=[], 
			total_win=[],
			)

	if step_result == []:
		return render_template('tendency_by_volume.html', 
			result_set=[], 
			other_result=[], 
			total_los=[], 
			total_win=[],
			start=start,
			end=end
		)

	return render_template('tendency_by_volume.html', 
		result_set = result, 
		other_result = step_result['step_detail'],
		total_win = step_result['total_win'],
		total_los = step_result['total_los'],
		start=start,
		end=end)

@app.route('/prize/', methods=['POST', 'GET'])
def get_prize_result():
	try:
		start = request.args['start_date']
		end = end_date_plus(request.args['end_date'])
		result = get_result(GET_PRIZE, [start, end])
	except:
		result = []
		current_date = datetime.datetime.now().strftime('%Y-%m-%d')
		return render_template('prize_result.html', 
			result_set=[], 
			other_result=[],
			start=current_date,
			end=current_date)

	print('ok')
	print(result)
	return render_template('prize_result.html', result_set = result, start=start, end=request.args['end_date'])


def get_result(method_type, args):
	conn = sqlite3.connect(DATABASE_FILE_NAME)
	cursor = conn.cursor()

	if method_type == BY_DATE:
		exe_sql = "SELECT * FROM RESULT r where r.PREDRAWTIME like '%{0}%' order by r.predrawtime".format(args)
	elif method_type == BY_PERIOD:
		exe_sql = "SELECT * FROM RESULT r where r.PREDRAWTIME >= '{0}' and r.PREDRAWTIME <= '{1}' order by r.predrawtime".format(args[0],args[1])
	elif method_type == BY_VOLUME:
		exe_sql = "SELECT * FROM RESULT  where PREDRAWISSUE >= {0} and PREDRAWISSUE <= {1} order by predrawtime".format(args[0],args[1])
	elif method_type == GET_PRIZE:
		exe_sql = "SELECT * FROM RESULT r where r.PREDRAWTIME >= '{0}' and r.PREDRAWTIME <= '{1}' order by r.predrawtime".format(args[0],args[1])
	else:
		return []

	result = []
	print(exe_sql)
	for row in cursor.execute(exe_sql):
		prize_result = {}

		prize_result['abet_id'] = row[3]
		prize_result['bbet_code'] = row[1]
		prize_result['cbet_time'] = row[4]

		result.append(prize_result)
	conn.close()

	return result

def end_date_plus(date_string):
	return (datetime.datetime.strptime(date_string, '%Y-%m-%d').date()+timedelta(days=1)).__str__()

@app.route('/')
def show_entries():
	return render_template('index.html')

@app.route('/setting/get/')
def get_setting():
	conn = sqlite3.connect(DATABASE_FILE_NAME)
	cursor = conn.cursor()
	exe_sql = "SELECT PARAM_VALUE FROM SETTINGS WHERE PARAM='LAST_UPDATED' OR PARAM='MAX_BET' OR PARAM='CURRENT_RULE' OR PARAM='RULE_TWO_BET'"
	cursor.execute(exe_sql)
	data = cursor.fetchall()
	conn.close()
	return render_template('setting.html', max_bet=data[0][0], last_updated=data[1][0], rule=int(data[3][0]), rule_two=data[2][0])

@app.route('/setting/update_max_bet')
def update_max_bet():
	conn = sqlite3.connect(DATABASE_FILE_NAME)
	cursor = conn.cursor()
	max_bet = int(request.args['max_bet'])
	exe_sql = 'UPDATE SETTINGS SET PARAM_VALUE={0} WHERE PARAM="MAX_BET"'.format(max_bet)
	print(exe_sql)
	cursor.execute(exe_sql)
	conn.commit()
	conn.close()
	return render_template('setting.html', max_bet=max_bet)

@app.route('/setting/update_ruletwo')
def update_ruletwo():
	conn = sqlite3.connect(DATABASE_FILE_NAME)
	cursor = conn.cursor()
	rule_two = request.args['rule_two']
	exe_sql = 'UPDATE SETTINGS SET PARAM_VALUE="{0}" WHERE PARAM="RULE_TWO_BET"'.format(rule_two)
	print(exe_sql)
	cursor.execute(exe_sql)
	conn.commit()
	conn.close()
	return render_template('setting.html', rule_two=rule_two)

@app.route('/setting/update/')
def update_database():
	conn = sqlite3.connect(DATABASE_FILE_NAME)
	cursor = conn.cursor()
	exe_sql = "SELECT PARAM_VALUE FROM SETTINGS WHERE PARAM='LAST_UPDATED' OR PARAM='MAX_BET'"
	cursor.execute(exe_sql)
	data = cursor.fetchall()
	conn.close()

	update_result = update_the_database()
	if update_result:
		return render_template('setting.html', max_bet=data[0][0], update_result=update_result, last_updated=datetime.datetime.now().strftime('%Y-%m-%d'))
	else:
		return render_template('setting.html', max_bet=data[0][0], update_result=update_result, last_updated=data[1][0], )

@app.route('/setting/update_rule/')
def update_rule():
	conn = sqlite3.connect(DATABASE_FILE_NAME)
	cursor = conn.cursor()
	rule = int(request.args['rule'])
	exe_sql = 'UPDATE SETTINGS SET PARAM_VALUE={0} WHERE PARAM="CURRENT_RULE"'.format(rule)
	print(exe_sql)
	cursor.execute(exe_sql)
	conn.commit()
	conn.close()
	return render_template('setting.html', rule=rule)

if __name__ == '__main__':
	app.run(debug=True)