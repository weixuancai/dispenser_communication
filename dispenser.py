# import Configparser as cf

# config = cf.ConfigParser()
# # print config['EE_06_01']
# config.readfp(open('communication.conf'))

import time,datetime

import pymongo
from pymongo import MongoClient

import json,urllib2
from bson.objectid import ObjectId

import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

import logging

with open('communication.json') as json_data_file:
    conf = json.load(json_data_file)
logging.basicConfig(filename='logfile.log',format='%(asctime)s - %(message)s',level=logging.ERROR)

#API SERVER
login_api = 'https://smartcampus.et.ntust.edu.tw:5417/v1/login'
login_body={'username':'sc_user001',
            'password':'dispenser'}
get_api = 'https://smartcampus.et.ntust.edu.tw:5417/v1/dispenser/rawdata?Device_ID='
destination = 'https://smartcampus.et.ntust.edu.tw:5417/v1/smartcampus/dispenser/rawdata'
timeout_counter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

def run():
    global timeout_counter
    for i in conf:
        try:
            page1 = 'http://' + i[u'IP'] + '/protect/home.htm'
            page2 = 'http://' + i[u'IP'] + '/protect/index2.htm'
            Auth = HTTPBasicAuth(i[u'Account'],i[u'Password'])
            res = requests.get(page1, auth=Auth,timeout=5)
            res_2 = requests.get(page2, auth=Auth,timeout=5)
            soup = BeautifulSoup(res.text,'html.parser')
            soupp = BeautifulSoup(res_2.text,'html.parser')

        except requests.exceptions.Timeout:
            logging.error("Timeout occurred : " + i[u'Device_ID'],exc_info = True)
            timeout_counter[i[u'Number']] = timeout_counter[i[u'Number']] + 1
            # print timeout_counter
            if(timeout_counter[i[u'Number']] > 4):
                data = get(i[u'Device_ID'])
                conn_mongo(i[u'Building'],data)
                post(data)
                timeout_counter[i[u'Number']] = 0
    
        except Exception as e:
            device_id = i[u'Device_ID']
            logging.error("Exception occurred : " + device_id,exc_info = True)
            data = get(device_id)
            conn_mongo(i[u'Building'],data)
            post(data)
        else:
            status = 1
            hardware = 'PCB'
            device_id = i[u'Device_ID']
            mac_address = i[u'Mac']
            #Time
            time_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time_stamp = int(round(time.time() * 1000))
            #Status
            hottemp = int(soup.find(attrs={'name':'textfield[0]'}).attrs['value'])
            warmtemp = int(soup.find(attrs={'name':'textfield[1]'}).attrs['value'])
            coldtemp = int(soup.find(attrs={'name':'textfield[2]'}).attrs['value'])
            HotTemp_Insulation = int(soup.find(attrs={'name':'textfield[3]'}).attrs['value'])
            WarmTemp_Insulation = int(soup.find(attrs={'name':'textfield[4]'}).attrs['value'])
            ColdTemp_Insulation = int(soup.find(attrs={'name':'textfield[5]'}).attrs['value'])
            TDS = int(soup.find(attrs={'name':'textfield[8]'}).attrs['value'])
            ErrorCode = int(soup.find(attrs={'name':'textfield[7]'}).attrs['value'])
            #Flag
            SavingPower = int(soup.find('input',attrs={'name':'lights1'}).has_attr('checked'))
            Sterilizing = int(soup.find('input',attrs={'name':'lights3'}).has_attr('checked'))
            Heating = int(soupp.find('input',attrs={'name':'lights13'}).has_attr('checked'))
            Cooling = int(soupp.find('input',attrs={'name':'lights14'}).has_attr('checked'))
            HighLevel = unicode(int(soupp.find('input',attrs={'name':'lights10'}).has_attr('checked')))
            MidLevel = unicode(int(soupp.find('input',attrs={'name':'lights11'}).has_attr('checked')))
            LowLevel = unicode(int(soupp.find('input',attrs={'name':'lights12'}).has_attr('checked')))


            AllLevel = int(HighLevel) + int(MidLevel) + int(LowLevel)
            if AllLevel == 3:
                WaterLevel = 22
            elif AllLevel == 2:
                WaterLevel = 15
            else:
                WaterLevel = 10

            InputWater = int(soupp.find('input',attrs={'name':'lights15'}).has_attr('checked'))
            HotOutput = int(soupp.find('input',attrs={'name':'lights16'}).has_attr('checked'))
            WarmOutput = int(soupp.find('input',attrs={'name':'lights17'}).has_attr('checked'))
            ColdOutput = int(soupp.find('input',attrs={'name':'lights18'}).has_attr('checked'))

            data = {"UploadTime": time_string,
            "Mac_Address":mac_address,
            "Status":status,
            "Hardware":hardware,
            "TimeStamp":time_stamp,
            "Device_ID":device_id,
            "HotTemp":hottemp,
            "WarmTemp":warmtemp,
            "ColdTemp":coldtemp,
            "Heating":Heating,
            "Cooling":Cooling,
            "Refilling":InputWater,
            "WaterLevel":WaterLevel,
            "TDS":TDS,
            "Hot_Valve":HotOutput,
            "Warm_Valve":WarmOutput,
            "Cold_Valve":ColdOutput,
            "SavingPower":SavingPower,
            "Sterilizing":Sterilizing,
            "ErrorCode":ErrorCode,
            "HotTemp_Insulation":HotTemp_Insulation,
            "WarmTemp_Insulation":WarmTemp_Insulation,
            "ColdTemp_Insulation":ColdTemp_Insulation
            }
            # j_data = json.dumps(data)
            print "         |",time_string,"|"
            conn_mongo(i[u'Building'],data)
            post(data)
            print "========================================================================"

def get(device_id):
    # print "get"
    get_url = get_api + device_id
    try:
        res_err = requests.get(get_url)
    except Exception as err_get:
        logging.error("GET")
        logging.error(err_get,exc_info=True)
    else:
        newest_data = res_err.json()
        data = {"UploadTime": newest_data[u'UploadTime'],
        "Mac_Address":newest_data[u'Mac_Address'],
        "Status":-1,
        "Hardware":newest_data[u'Hardware'],
        "TimeStamp":newest_data[u'TimeStamp'],
        "Device_ID":newest_data[u'Device_ID'],
        "HotTemp":newest_data[u'HotTemp'],
        "WarmTemp":newest_data[u'WarmTemp'],
        "ColdTemp":newest_data[u'ColdTemp'],
        "Heating":newest_data[u'Heating'],
        "Cooling":newest_data[u'Cooling'],
        "Refilling":newest_data[u'Refilling'],
        "WaterLevel":newest_data[u'WaterLevel'],
        "TDS":newest_data[u'TDS'],
        "Hot_Valve":newest_data[u'Hot_Valve'],
        "Warm_Valve":newest_data[u'Warm_Valve'],
        "Cold_Valve":newest_data[u'Cold_Valve'],
        "SavingPower":newest_data[u'SavingPower'],
        "Sterilizing":newest_data[u'Sterilizing'],
        "ErrorCode":newest_data[u'ErrorCode'],
        "HotTemp_Insulation":newest_data[u'HotTemp_Insulation'],
        "WarmTemp_Insulation":newest_data[u'WarmTemp_Insulation'],
        "ColdTemp_Insulation":newest_data[u'ColdTemp_Insulation']
        }
        # j_data = json.dumps(data)
        return data

def post(data):

    j_data = json.dumps(data)
    try:
        response_login = requests.post(login_api, data=json.dumps(login_body))
        token = response_login.json()[u'token']
        requests_god_headers = {"Authorization":token,
                                "Content-Type":"application/json"}
        
        try:
            # Post to GodServer
            response_god = requests.post(destination, data=j_data,headers=requests_god_headers)
        except Exception as err_post:
            logging.error("POST")
            logging.error(j_data)
            logging.error(err_post,exc_info=True)
        else:
            print data[u'Device_ID'],"| API SERVER | Status = ",response_god.status_code
    except Exception as err_login:
        logging.error("LOGIN")
        logging.error(err_login,exc_info=True)

def conn_mongo(collection_name,data):
    url = "mongodb://140.118.123.95"
    conn = MongoClient(url)
    db = conn.dispenser_board
    the_coll =  collection_name.encode('ascii','ignore')
    collection = db[''+the_coll] 
    try:
        # Post to Backup Server
        response_powerful2 = collection.insert_one(data)
    except Exception as err_mongo:
        logging.error("POST Mongo")
        logging.error(data)
        logging.error(err_mongo,exc_info=True)
    else:
        del data['_id']
        print data[u'Device_ID'],"| BACKUP     | Status = OK"

while(True):
    run()
    time.sleep(30)