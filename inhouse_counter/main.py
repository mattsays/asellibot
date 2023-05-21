import json
from scapy.all import srp,Ether,ARP,conf 
import requests
import schedule
import time

BASE_IP = "192.168.1.0/24"
INTERFACE = "wlan0"
conf.verb = False
previous_data = '{"in_house": []}'

def populate_data_dict(path: str):
    with open(path) as f:
        return json.load(f)

def get_connected_devices():
    devices = []
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst = BASE_IP), 
		     timeout = 2, 
		     iface = INTERFACE,
		     inter = 0.1)

    for _,rcv in ans: 
        devices.append(rcv.sprintf(r"%Ether.src%"))
    return devices

def get_inhouse_people_json():
    global json_data
    people = []
    devices = get_connected_devices()

    for device in devices:
        for username in json_data["members"].keys():
            if username in people:
                continue
            elif device in json_data["members"][username]:
                people.append(username)

    return json.dumps({"in_house": people})

json_data = populate_data_dict("./config.json")

def send_inhouse_update():
    global json_data
    global previous_data
    
    people = get_inhouse_people_json()
    if previous_data == people:
        return

    previous_data = people

    r= requests.post(f"{ json_data['base_url'] }/{ json_data['token'] }/in_house/", data=people)
    print(f"Sent inhouse update with status code: {r.status_code}")


print("Starting...")
schedule.every(5).minutes.do(send_inhouse_update) # Time is in UTC format
while True:
    schedule.run_pending()
    time.sleep(1)
        

