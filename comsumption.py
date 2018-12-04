# import Configparser as cf

# config = cf.ConfigParser()
# # print config['EE_06_01']
# config.readfp(open('communication.conf'))

import time,datetime

# import pymongo
# from pymongo import MongoClient

import json,urllib2
from bson.objectid import ObjectId

import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

import logging

with open('communication.json') as json_data_file:
    conf = json.load(json_data_file)
logging.basicConfig(filename='comsumption.log',format='%(asctime)s - %(message)s',level=logging.ERROR)


def run():
    # global timeout_counter
    try:
        # page1 = 'http://' + i[u'IP'] + '/protect/home.htm'
        page2 = 'http://http://140.118.122.116/protect/index2.htm'
        Auth = HTTPBasicAuth('Admin','Admin0000')
        # res = requests.get(page1, auth=Auth,timeout=5)
        res_2 = requests.get(page2, auth=Auth,timeout=5)
        # soup = BeautifulSoup(res.text,'html.parser')
        soupp = BeautifulSoup(res_2.text,'html.parser')

    except requests.exceptions.Timeout:
        print(e)
        # logging.error("Timeout occurred : " + i[u'Device_ID'],exc_info = True)
        # timeout_counter[i[u'Number']] = timeout_counter[i[u'Number']] + 1
        # # print timeout_counter
        # if(timeout_counter[i[u'Number']] > 4):
        #     data = get(i[u'Device_ID'])
        #     conn_mongo(i[u'Building'],data)
        #     post(data)
        #     timeout_counter[i[u'Number']] = 0

    except Exception as e:
        print(e)
        # device_id = i[u'Device_ID']
        # logging.error("Exception occurred : " + device_id,exc_info = True)
        # data = get(device_id)
        # conn_mongo(i[u'Building'],data)
        # post(data)
    else:
        HotOutput = int(soupp.find('input',attrs={'name':'lights16'}).has_attr('checked'))
        WarmOutput = int(soupp.find('input',attrs={'name':'lights17'}).has_attr('checked'))
        ColdOutput = int(soupp.find('input',attrs={'name':'lights18'}).has_attr('checked'))
        print(HotOutput)


while(True):
    run()
    time.sleep(1)