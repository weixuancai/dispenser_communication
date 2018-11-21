import os
import json
import subprocess

with open('communication.json') as json_data_file:
    conf = json.load(json_data_file)

def check_ping():
    hostname = "google.com"
    ip = "140.118.121.2"
    for i in conf:
        ip = i[u'IP']
        print ip
        response = os.system("ping -c 1 " + ip)
    # and then check the response...
        if response == 0:
            pingstatus = "Network Active"
        else:
            pingstatus = "Network Error"
        print pingstatus
    # return pingstatus

# check_ping()
hostname = "google.com"
def ping():
    out = subprocess.check_output("ping -c 1 " + hostname)
ping()
