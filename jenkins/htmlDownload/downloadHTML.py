import urllib3
import os

START_URL = 'https://jenkins-opensubmit.192.168.99.100.nip.io/job/Test/37/valgrindResult/pid=1013'
USERNAME = 'developer-admin'
PASSWORD = 'e9dd8ba9b4287266e28594cb6353a65d'
DOMAIN = START_URL.replace('https://', '').replace('http://', '').split('/')[0]

http = urllib3.PoolManager()
headers = urllib3.util.make_headers(basic_auth=USERNAME + ':' + PASSWORD)


def download_page(url):
    r = http.request('GET', url,
                     headers=headers)
    file = url.replace('https://', '').replace('http://', '')
    folder = file.rsplit('/', 1)[0]

    if not os.path.exists(folder):
        os.makedirs(folder)

    text_file = open(file + '.html', "w")
    text_file.write(r.data.decode('UTF-8'))
    text_file.close()


download_page(START_URL)
