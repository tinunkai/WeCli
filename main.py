import requests

param = {
    'token': 'xoxp-239158785445-239908733558-684388134196-bd82d5cd3f1a6c2ebbc59b67eb428fd6',
    'channels': 'D70ESM5PB',
    'filename': 'filename',
    'initial_comment': 'a file from python!',
}
files = {'file': open('main.py', 'rb')}
requests.post(url='https://slack.com/api/files.upload', params=param, files=files)
