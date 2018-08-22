import os
import time
from urllib import parse, request

import urllib3
from jenkins import Jenkins
from jenkins import JenkinsException

DEBUG = False

PIPELINE_CONFIG_URL = 'https://raw.githubusercontent.com/lukas15442/open-space/master/jenkins/pipelines/PipelineConfig.xml'

PIPELINE_REPO = 'https://github.com/lukas15442/open-space.git'
PIPELINE_BASE = 'jenkins/pipelines'
JENKINSFILE_NAME = 'jenkinsfile.groovy'

JENKINS_URL = 'https://jenkins-open-submit.apps.ocp.fbi.h-da.de'
JENKINS_USERNAME = 'api'
JENKINS_SECRET = 'b2607390ba3f4c7fc63f039d9987c2b7'

# Parameter that will be filled when debug is off
USERNAME = 'istlukoeh'
COURSE = 'PAD1'
ASSIGNMENT = 'Praktikum 1'
COURSE_AND_ASSIGNMENT = COURSE + '-' + ASSIGNMENT
JOB_NAME = COURSE + '-' + ASSIGNMENT + '-' + USERNAME
FOLDER = '/tmp/1_3wrqhvuj/'


def validate(job):
    global FOLDER
    my_init(job)
    FOLDER = FOLDER[0:-1]

    if not DEBUG:
        job.working_dir = os.popen(
            'find ' + FOLDER + ' -maxdepth 1 -type d -not -path ' + FOLDER + '/__pycache__ -not -path ' + FOLDER + '') \
                              .read()[0:-1] + '/'
        job.run_make(mandatory=True)

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

    job_url = JENKINS_URL + '/job/' + parse.quote(JOB_NAME) + '/' + str(build_number)
    result = '<a href="' + job_url + '" target="_blank">Jenkins results</a>'
    success = 'Finished: SUCCESS' in build_output

    if success:
        print('Failed!')
    else:
        print('Success')

    print(result)

    if not DEBUG:
        if success:
            job.send_pass_result(result)
        else:
            job.send_fail_result(result)


def my_init(job):
    global USERNAME
    global COURSE
    global ASSIGNMENT
    global FOLDER
    global COURSE_AND_ASSIGNMENT
    global JOB_NAME
    if not DEBUG:
        USERNAME = job.submitter_student_id
        COURSE = job.course
        ASSIGNMENT = job.assignment
        FOLDER = job.working_dir
        COURSE_AND_ASSIGNMENT = COURSE + '-' + ASSIGNMENT
        JOB_NAME = COURSE + '-' + ASSIGNMENT + '-' + USERNAME

        os.system('scp -i /ssh/key -r ' + FOLDER + ' jenkins-ssh@jenkins-ssh:/opensubmit')
        os.system('chmod -R 777 ' + FOLDER)

    os.environ['PYTHONHTTPSVERIFY'] = '0'
    urllib3.disable_warnings()


def create_pipeline(jenkins_server):
    # data = request.urlopen(
    #    PIPELINE_BASE_URL + parse.quote(COURSE) + '/' + parse.quote(ASSIGNMENT) + '.xml')
    data = request.urlopen(PIPELINE_CONFIG_URL)
    xml_file = data.read().decode("utf-8")
    xml_file = xml_file.replace('{USERNAME}', USERNAME)
    xml_file = xml_file.replace('{GIT_REPO}', PIPELINE_REPO)
    xml_file = xml_file.replace('{GIT_JENKINSFILE_PATH}',
                                PIPELINE_BASE + '/' + COURSE + '/' + ASSIGNMENT + '/' + JENKINSFILE_NAME)

    try:
        jenkins_server.create_job(JOB_NAME, xml_file)
    except JenkinsException:
        print('Pipeline already exists')


if DEBUG:
    validate(None)
