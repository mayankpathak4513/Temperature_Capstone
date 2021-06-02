#This code helps in main working and running of the set-up.

import conf, json, time, math, statistics, requests
from boltiot import Bolt

def compute_bounds(history_data, frame_size, factor):
	if len(history_data)<frame_size:
		return None
	if len(history_data)>frame_size:
		del history_data[0:len(history_data)-frame_size-1]
	Mn = statistics.mean(history_data)
	Variance = 0
	for data in history_data:
		Variance += math.pow((data-Mn),2)
	Zn = factor*math.sqrt(Variance/frame_size)
	High_bound = history_data[frame_size-1]+Zn
	Low_bound= history_data[frame_size - 1]- Zn
	return [High_bound, Low_bound]

mybolt = Bolt(conf.api_key, conf.device_id)
history_data = []

def send_telegram_message(message):
	url = "https://api.telegram.org/" + conf.telegram_bot_id + "/sendMessage"
	data = {"chat_id": conf.telegram_chat_id, "text": message}
	try:
		response= requests.request("POST", url, params = data)
		print("This is the Telegram response")
		print(response.text)
		telegram_data = json.loads(response.text)
		return telegram_data["ok"]
	except Exception as e:
		print("An error occurredin sending the alert message via Telegram")
		print(e)
		return False

def buzzer_alert():
	high_response = mybolt.digitalWrite("2", "HIGH")
	print(high_response)
	time.sleep(5)
	low_response = mybolt.digitalWrite("2", "LOW")
	print(low_response)
	time.sleep(5)


def check_temperature(value,checker):
	if value > conf.threshold[2]:
		print("The temperaure value increased the threshold value. Sending an alert notification")
		message = "Temperature increased the threshold value. The current value is: " + str(int(sensor_value*0.097))
		telegram_status = send_telegram_message(message)
		print("This is the Telegram status", telegram_status)
		if not checker:
			return buzzer_alert()
		if checker:
			return 0

	if value < conf.threshold[0]:
		print("The temperature value  decreased below the threshold value. Sending an alert notification")
		message = "Temperature decreased below the threshold value. The current value is: " + str(int(sensor_value*0.097))
		telegram_status = send_telegram_message(message)
		print("This is the Telegram status", telegram_status)
		if not checker:
			return buzzer_alert()
		if checker:
			return 0

	if value > conf.threshold[0] and value < conf.threshold[1]:
		print("The temperature value is between ",str(int(conf.threshold[0]*0.097))," and ",str(int(conf.threshold[1]*0.097)), ". Sending an alert notification")
		message = "Temperature is between " + str(int(conf.threshold[0]*0.097)) + " and " + str(int(conf.threshold[1]*0.097)) + ". Check prediction table. The current value is: " + str(int(sensor_value*0.097))
		telegram_status = send_telegram_message(message)
		print("This is the Telegram status", telegram_status)
		if not checker:
			return buzzer_alert()
		if checker:
			return 0

	if value > conf.threshold[1] and value < conf.threshold[2]:
		if not checker:
			time.sleep(10)
		if checker:
			return 0


while True:
	checker = False
	response = mybolt.analogRead('A0')
	data = json.loads(response)
	if data['success'] != 1:
		print("There was an error while retriving the data")
		print("This is the error:" +data['value'])
		time.sleep(10)
		continue
	print("This is the value: " +data['value'])

	sensor_value = 0
	try:
		sensor_value = int(data['value'])
	except e:
		print("There was an error while parsing the response: ",e)
		continue

	bound= compute_bounds(history_data, conf.frame_size, conf.mul_factor)
	if not bound:
		required_data_count = conf.frame_size-len(history_data)
		print("Not enough data to compute Z-score. Need ",required_data_count," more data points")
		history_data.append(int(data['value']))
		check_temperature(sensor_value, checker)
		continue

	try:
		if sensor_value> bound[0]:
			print("The temperature value increased suddenly. Sending an alert notification")
			message = "Temperature increased suddenly. The current value is: " + str(int(sensor_value*0.097))
			telegram_status = send_telegram_message(message)
			print("This is the Telegram status", telegram_status)
			buzzer_alert()
			checker = True
		elif sensor_value< bound[1]:
			print("The temperature value decreased suddenly. Sending an alert notification")
			message = "Temperature decreased suddenly. The current value is: " + str(int(sensor_value*0.097))
			telegram_status = send_telegram_message(message)
			print("This is the Telegram status", telegram_status)
			buzzer_alert()
			checker = True
		check_temperature(sensor_value, checker)
		history_data.append(sensor_value)
	except Exception as e:
		print("error", e)
