import os
import time

import requests
from jenkins import Jenkins

URL = 'https://jenkins-jenkins.192.168.99.100.nip.io'
USERNAME = 'restapiuser-admin'
PASSWORD = '605624ad2448b011a50f60dac9b1e1b6'
JOB = 'Test'
FOLDER = 'testing'

os.environ['PYTHONHTTPSVERIFY'] = '0'
requests.packages.urllib3.disable_warnings()

server = Jenkins(URL, USERNAME, PASSWORD)

job = False

queue_number = server.build_job(JOB, {'folder': FOLDER})
queue_item = server.get_queue_item(queue_number)

while 'executable' not in queue_item:
    print('Waiting for queue item . . .')
    time.sleep(2)
    queue_item = server.get_queue_item(queue_number)

build_number = queue_item['executable']['number']

build_output = server.get_build_console_output(JOB, build_number)
while build_output.split('\n')[-2] != 'Finished: SUCCESS':
    print('Waiting for complete pipeline output . . .')
    time.sleep(2)
    build_output = server.get_build_console_output(JOB, build_number)

print(build_output)
