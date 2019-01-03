import subprocess
import sys
import json

with open('gw.json') as json_data_file:
    conf = json.load(json_data_file)
# list fail
fail = list()
fail_ip = list()

def ping():
    for i in conf:
        host = i[u'IP']
        # cmd = ['ping', '-c2', '-W 5', host ]
        cmd = ['ping', '-c1', host ]
        # print cmd
        done = False
        timeout = 1 # default time out after ten times, set to -1 to disable timeout

        print i[u'Device_ID']," : Ping ...",
        while not done and timeout:
                response = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                stdout, stderr = response.communicate()
                if response.returncode == 0:
                    print "OK"
                    done = True
                else:
                    # sys.stdout.write('.')
                    timeout -= 1
                    fail.append(str(i[u'Device_ID']))
                    fail_ip.append(str(i[u'IP']))
                    
        if not done:
            print "Failed to respond"

ping()
print "==========================================================="
for index,item in enumerate(fail):
    print item," | ",fail_ip[index]
