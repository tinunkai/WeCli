import requests
from datetime import datetime

import itchat
from itchat.content import *
import colorful
import json

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

def print_cmd_qr(qrText, enableCmdQR=True):
    up_half = '\u2580'
    down_half = '\u2584'
    full_block = '\u2588'
    blank = ' '
    qr = qrText.strip().split('\n')
    qr = [list(map(int, row)) for row in qr]
    qr = list(map(list, zip(*qr)))
    qr_block = ['' for _ in range((len(qr[0]) + 1) // 2)]
    for i in range(len(qr)):
        for j in range(0, len(qr[0]), 2):
            if len(qr[i][j:j+2]) == 2:
                block = qr[i][j:j+2]
            else:
                block = qr[i][j:j+2] + [1]
            if block == [0, 0]:
                qr_block[j//2] += full_block
            elif block == [1, 0]:
                qr_block[j//2] += down_half
            elif block == [0, 1]:
                qr_block[j//2] += up_half
            elif block == [1, 1]:
                qr_block[j//2] += blank
    printc('\n'.join(qr_block))

def printc(content, bg='#000000', fg='#ffffff'):
    colorful.use_palette({'fg': fg, 'bg': bg})
    print(colorful.fg_on_bg(str(content)))

if __name__ == '__main__':
    main()
