import random
from collections import defaultdict
import sqlite3
import math

rebate = 19.4
money = 10
DATABASE_FILE_NAME = 'result.db'

def get_choice(arr):
	if arr[0] > arr[1]:
		best_choice = (arr[0] + arr[1]) % 10
		return best_choice if best_choice else 10
	else:
		return arr[1] - arr[0]

def get_prise(choice, result):
	_prise = []

	for index, x in enumerate(choice):
		if x[-1] != -1 and x[0] in result[0:5]:
			_prise.append(index)

	return _prise

def failure_increment(choice, bet):
	for x in choice:
		if x[-1] != -1:
			x[-2] += 1
			if x[-2] > bet:
				x[-1] = -1

def get_win(win_list, choice):
	__win = 0.0
	for x in win_list:
		__win = __win + rebate * (2 ** choice[x][-2])

	return __win

def get_lost(choice):
	__lost = 0.0
	for x in choice:
		if x[-1] != -1:
			__lost = __lost + money * (2 ** x[-2])

	return __lost

def get_bet_process_detail(prise):
	with sqlite3.connect(DATABASE_FILE_NAME) as conn:
		cursor = conn.cursor()
		exe_sql = 'SELECT PARAM_VALUE FROM SETTINGS WHERE PARAM="CURRENT_RULE"'
		cursor.execute(exe_sql)
		rule = int(cursor.fetchone()[0])


	if rule == 1:
		return rule_one(prise)
	else:
		return rule_two(prise)

def rule_one(prise):
	if prise == []:
		return []
	conn = sqlite3.connect(DATABASE_FILE_NAME)
	cursor = conn.cursor()
	exe_sql = 'SELECT PARAM_VALUE FROM SETTINGS WHERE PARAM="MAX_BET"'
	cursor.execute(exe_sql)
	max_bet = int(cursor.fetchone()[0])
	conn.close()

	result = defaultdict(list)
	choicess = []
	max_failure = 0
	choices = get_choice(prise[0])

	choicess.append([choices, 0, 0])
	total_win = []
	total_los = []
	win = 0.0
	los = 0.0
	for x in prise[1:]:
		process = {}

		process['prize'] = x

		bet_detail = ""
		for bet in choicess:
			if bet[-1] != -1:
				bet_detail = bet_detail + "号码：{0}, 倍数：{1}###".format(bet[0], bet[1]+1)
		process['details'] = bet_detail		

		current_los = 0.0
		current_win = 0.0
		current_los = get_lost(choicess)

		current_prise_result = get_prise(choicess, x)
		if current_prise_result:
			current_win = get_win(current_prise_result, choicess)
			for index in current_prise_result:
				choicess[index][-1] = -1

		process['current_lost'] = round(current_los, 2)
		process['current_win']  = round(current_win, 2)
		win = win + current_win
		los = los + current_los
		total_win.append(round(win, 2))
		total_los.append(round(los, 2))
		choicess = remove_item(choicess)
		failure_increment(choicess, max_bet)
		choicess.append([get_choice(x), 0, 0])
		result['step_detail'].append(process)

	if 'step_detail' not in result:
		result['step_detail'] = []

	result['total_win'] = total_win
	result['total_los'] = total_los

	return result

def remove_item(invalid_item):
	res = []

	for item in invalid_item:
		if item[-1] == -1:
			res.append(item)

	for item in res:
		invalid_item.remove(item)

	return invalid_item


def get_rule_two_choice(choice):
	if choice[0] > choice[1]:
		return (choice[0] + choice[1]) % 10 if (choice[0] + choice[1]) != 10 else 10
	else:
		return abs(choice[0] - choice[1])

def rule_two(prise):
	if prise == []:
		return []

	conn = sqlite3.connect(DATABASE_FILE_NAME)
	cursor = conn.cursor()
	exe_sql = 'SELECT PARAM_VALUE FROM SETTINGS WHERE PARAM="RULE_TWO_BET"'
	cursor.execute(exe_sql)
	rule_times = list(map(int, cursor.fetchone()[0].split(',')))
	conn.close()

	result = defaultdict(list)
	max_failure = 0
	choices = get_rule_two_choice(prise[0])

	total_win = []
	total_los = []
	win = 0.0
	los = 0.0
	runtime_index = 0

	for x in prise[1:]:
		process = {}

		process['prize'] = x

		bet_detail = "号码：{0}, 投注金额：{1}".format(choices, rule_times[runtime_index]*7)
		process['details'] = bet_detail		

		current_los = 0.0
		current_win = 0.0
		
		if choices in x[0:7]:
			current_win = rule_times[runtime_index] * 9.93
			current_los = rule_times[runtime_index] * 7
			runtime_index = 0
		else:
			current_los = rule_times[runtime_index] * 7
			runtime_index += 1

		if runtime_index >= len(rule_times):
			runtime_index = 0

		choices = get_rule_two_choice(x)

		process['current_lost'] = round(current_los, 2)
		process['current_win']  = round(current_win, 2)
		win = win + current_win
		los = los + current_los
		total_win.append(round(win, 2))
		total_los.append(round(los, 2))

		result['step_detail'].append(process)

	if 'step_detail' not in result:
		result['step_detail'] = []

	result['total_win'] = total_win
	result['total_los'] = total_los

	return result

if __name__ == '__main__':
	prise = [
			[5,8,6,9,4,10,2,7,1,3],
			[6,8,4,1,9,10,3,5,7,2],
			[7,10,3,4,5,6,8,1,2,9],
			[4,5,7,1,9,10,6,8,3,2],
			[10,8,9,3,2,7,4,6,5,1],
			[8,6,1,10,9,3,4,7,2,5],
			[2,6,8,4,5,3,1,10,7,9],
			[10,5,3,1,6,7,4,2,8,9],
			[9,2,4,1,10,8,7,5,3,6],
			[7,2,1,6,8,9,10,3,4,5],
			[3,2,1,4,10,8,6,5,7,9],
			[3,1,2,4,9,10,8,6,7,5],
			[4,1,10,3,5,2,7,8,9,6],
			[2,6,1,8,4,7,3,9,5,10],
			[9,7,6,3,10,2,5,1,4,8],
			[5,3,2,6,10,4,8,7,9,1],
			[7,1,5,10,6,9,4,8,2,3],
			[9,7,10,2,1,3,8,4,5,6],
			[2,4,9,3,10,8,5,1,6,7],
			[5,8,6,7,2,10,1,9,4,3],
			[6,7,8,2,10,3,9,5,1,4],
			[5,6,1,7,3,4,9,8,10,2],
			[9,5,4,3,2,8,1,6,7,10],
			[7,5,10,8,9,4,6,1,3,2],
			[8,7,3,4,5,9,1,10,2,6],
			[3,10,7,5,1,9,6,4,8,2],
			[8,6,9,7,2,10,5,4,3,1],
			[8,5,6,7,10,9,2,1,4,3]
			]
	print(rule_two(prise))