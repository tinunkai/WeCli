import requests
from datetime import datetime

import itchat
from itchat.content import *
import json

from utils import print_cmd_qr

@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING], isGroupChat=True, isFriendChat=True, isMpChat=True)
def text_msg(msg):
    print(datetime.fromtimestamp(msg['CreateTime']))
    print(msg)

@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def files(msg):
    print(datetime.fromtimestamp(msg['CreateTime']))
    print(msg)
    with open('slack.token.json', 'r') as f:
        param = json.load(f)
    files = {'file': msg.download(None)}
    requests.post(url='https://slack.com/api/files.upload', params=param, files=files)

def main():
    itchat.utils.print_cmd_qr = print_cmd_qr
    itchat.auto_login(enableCmdQR=2, hotReload=True)
    itchat.run()

if __name__ == '__main__':
    main()
