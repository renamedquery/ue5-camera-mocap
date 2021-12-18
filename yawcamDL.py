import urllib.request, time

URL_TO_DOWNLOAD = 'http://172.24.16.12:8888/out.jpg'

while (1):
    try:
        urllib.request.urlretrieve(URL_TO_DOWNLOAD, 'out.jpg')
        time.sleep(1/20)
    except PermissionError:
        print('PERMISSION DENIED AT {}'.format(time.time()))