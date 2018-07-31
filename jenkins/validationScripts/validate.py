import os
import time
from urllib import parse, request

import urllib3
from jenkins import Jenkins
from jenkins import JenkinsException

DEBUG = False

PIPELINE_BASE_URL = 'https://raw.githubusercontent.com/lukas15442/open-space/master/jenkins/pipelines/'
JENKINS_URL = 'https://jenkins-opensubmit.192.168.99.100.nip.io'
JENKINS_USERNAME = 'l.koehler'
JENKINS_SECRET = '94457fadc3ee1937a48af8175de6e4d4'

# Parameter that will be filled when debug is off
USERNAME = 'istlukoeh'
COURSE = 'PAD1'
ASSIGNMENT = 'Praktikum 1'
COURSE_AND_ASSIGNMENT = COURSE + '-' + ASSIGNMENT
JOB_NAME = COURSE + '-' + ASSIGNMENT + '-' + USERNAME
FOLDER = '/tmp/testing/'


def validate(job):
    my_init(job)

    server = Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_SECRET)
    create_pipeline(server)

    queue_number = server.build_job(JOB_NAME, {'folder': '/opensubmit/' + FOLDER.split('/')[2]})
    queue_item = server.get_queue_item(queue_number)

    while 'executable' not in queue_item or not queue_item['executable']:
        print('Waiting for queue item . . .')
        time.sleep(2)
        queue_item = server.get_queue_item(queue_number)

    while 'number' not in queue_item['executable'] or not queue_item['executable']['number']:
        print('Waiting for queue item . . .')
        time.sleep(2)
        queue_item = server.get_queue_item(queue_number)

    build_number = queue_item['executable']['number']

    build_output = server.get_build_console_output(JOB_NAME, build_number)
    while 'Finished:' not in build_output:
        print('Waiting for complete pipeline output . . .')
        time.sleep(2)
        build_output = server.get_build_console_output(JOB_NAME, build_number)

    print('Finished!')

    job_url = JENKINS_URL + '/job/' + parse.quote(JOB_NAME) + '/' + build_number
    print(job_url)

    if not DEBUG:
        job.send_pass_result(job_url)


def my_init(job):
    global USERNAME
    global COURSE
    global ASSIGNMENT
    global FOLDER
    if not DEBUG:
        USERNAME = job.submitter_student_id
        COURSE = job.course
        ASSIGNMENT = job.assignment
        FOLDER = job.working_dir

        os.system('chmod -R 777 ' + FOLDER)

    os.environ['PYTHONHTTPSVERIFY'] = '0'
    urllib3.disable_warnings()


def create_pipeline(jenkins_server):
    data = request.urlopen(
        PIPELINE_BASE_URL + parse.quote(COURSE) + '/' + parse.quote(ASSIGNMENT) + '.xml')
    xml_file = data.read().decode("utf-8").replace('{USERNAME}', USERNAME)

    try:
        jenkins_server.create_job(JOB_NAME, xml_file)
    except JenkinsException:
        print('Pipeline already exists')


if DEBUG:
    validate(None)
