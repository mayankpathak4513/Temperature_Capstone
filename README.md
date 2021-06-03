# Temperature_Capstone_Project

## Introduction :

The main scope of this project is to measure the temperature of a closed environment lets say we want to measure the temperature of a room.

Basically a range is fixed that is,the minimum and maximum temerature values are fixed and if the measured vaule is not in this range then the system alarms and sends a notification to the users device through SMS, email, telegram etc.

____________________________________

## Components required to work the project

1. Bolt WiFi Module(microcontroller)	

2. LED (generic)	

3. Buzzer-to alarm the area	

4. Jumper wires (generic)		

5. LM35-temperature sensor	

6. Breadboard (generic)

____________________________________
To do so you have to register at a platform called **Twillio** this will help us to get the notification on the device.
**Register --> confirm mobile number --> setup required function to carry-out --> Configure the file with the requireds private fields**

____________________________________

## Codes to implement the system

### 1. Config_code.py

```
#This code is used to config the Twillio with the device
#configurations and credential file

api_key = 'XXXXXX' # Enter your API Key used in Twillio App
device_id = 'BOLTXXXXXXX' # Enter the device id i.e. the Bolt Id
telegram_chat_id = '@XXXXXXX'
telegram_bot_id = 'botXXXXXXXX'
threshold = [206.186, 309.28, 412.38] #Change the threshold values according to your environment
frame_size = 10
mul_factor = 2
```

### 2. Main_code.py

```
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
```

### 3. Pediction_code.py

```
#This code helps in Predicting future instance values.

# Shows up the different Plots and can able to make comparisions.

setChartLibrary('google-chart');
setChartTitle('Polynomial Regression');
setChartType('predictionGraph');
setAxisName('time_stamp','temp');
mul(0.097);
setAnimation(true);
setCrosshair(true);
plotChart('time_stamp','analog');

```
Paper work is availabe at [The IJEAT Journal](http://www.ijeat.org/download/volume-9-issue-2/)

You can download the paper and view it by [clicking here🔗🔗](https://www.ijeat.org/wp-content/uploads/papers/v9i2/B2507129219.pdf)

### The project work is mainly to calculate the temperature of a closed environment and sends notification to the connected device through SMS, Mail, Telegram etc. only if the temperature of the region varies i.e., either the temperature increases(⬆) or the temperature decreases(⬇).

