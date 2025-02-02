from hassapi import Hass
import os
import yaml
from dotenv import load_dotenv
import datetime

load_dotenv()
hass = Hass(hassurl=os.getenv("HASS_URL"), token=os.getenv("HASS_TOKEN"))
summer = os.getenv("SUMMER", False)
if summer == "True":
    summer = True

with open('rooms_config.yml', 'r') as file:
    config = yaml.safe_load(file)

now = datetime.datetime.now().time()
outside_temp = float(hass.get_state(entity_id="weather.forecast_home").attributes["temperature"])
exp_times = [
    { "from": datetime.time(7, 30), "to": datetime.time(8, 30) },
    { "from": datetime.time(9, 30), "to": datetime.time(10, 30) },
    { "from": datetime.time(20, 30), "to": datetime.time(21, 30) },
    { "from": datetime.time(22, 30), "to": datetime.time(23, 30) },
]

def expensive(time):
    for exp_time in exp_times:
        if time >= exp_time["from"] and time <= exp_time["to"]:
            return True
    return False

for device in config:
    rule = config[device]
    room_temp = float(hass.get_state(entity_id=rule["room_temp_entity"]).state)
    also_in_summer = True if rule["also_in_summer"] == "True" else False
    if expensive(now) or room_temp >= float(rule["target_air_temperature"]) or (summer and not rule["also_in_summer"]):
        target_temp = 17
    else:
        target_temp =  float(rule["base_temp"]) + (20 - outside_temp) / 4 * float(rule["delta_ratio"])
        target_temp = min(target_temp, 27)
    target_temp = round(target_temp * 2) / 2
    if target_temp != float(hass.get_state(entity_id=device).attributes["temperature"]):
        hass.call_service(entity_id=device, service="set_temperature", temperature=target_temp)