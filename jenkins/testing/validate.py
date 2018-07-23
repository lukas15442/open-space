import os
import time

import requests
from jenkins import Jenkins


def validate(job):
    URL = 'https://jenkins-opensubmit.192.168.99.100.nip.io'
    USERNAME = 'developer-admin'
    PASSWORD = '69fcd7c0a6fdf5dad5b4f4e5292c8baf'
    JOB = 'Test'
    FOLDER = job.working_dir

    os.system('chmod -R 777 ' + FOLDER)

    os.environ['PYTHONHTTPSVERIFY'] = '0'
    requests.packages.urllib3.disable_warnings()

    server = Jenkins(URL, USERNAME, PASSWORD)

    queue_number = server.build_job(JOB, {'folder': '/opensubmit/' + FOLDER.split('/')[2]})
    queue_item = server.get_queue_item(queue_number)

    while 'executable' not in queue_item:
        print('Waiting for queue item . . .')
        time.sleep(2)
        queue_item = server.get_queue_item(queue_number)

    build_number = queue_item['executable']['number']

    build_output = server.get_build_console_output(JOB, build_number)
    while 'Finished:' not in build_output:
        print('Waiting for complete pipeline output . . .')
        time.sleep(2)
        build_output = server.get_build_console_output(JOB, build_number)

    print(build_output)

    job.send_pass_result(build_output)
