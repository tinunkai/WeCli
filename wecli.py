#!/usr/bin/env python3

from datetime import datetime
import time
import threading
import sys
import logging
import code
import atexit
import os
import re
import json
try:
    import readline
except:
    pass

import requests
import numpy as np
import itchat
import colorama

CQR = colorama.Fore.WHITE + colorama.Back.BLACK
CFRIEND = colorama.Fore.MAGENTA
CGROUP = colorama.Fore.CYAN
CRED = colorama.Fore.RED
CYELLOW = colorama.Fore.YELLOW
CGREEN = colorama.Fore.GREEN
CEND = colorama.Style.RESET_ALL

def print_cmd_qr(qrText, enableCmdQR=True):
    up_half = '\u2580'
    down_half = '\u2584'
    full_block = '\u2588'
    blank = ' '
    qr = qrText.split('\n')
    qr = list(list(map(int, row)) for row in qr[:-1])
    qr = list(map(list, zip(*qr)))
    qr_block = [list() for _ in range((len(qr[0]) + 1) // 2)]
    for i in range(len(qr)):
        for j in range(0, len(qr[0]), 2):
            if len(qr[i][j:j+2]) == 2:
                block = qr[i][j:j+2]
            else:
                block = qr[i][j:j+2] + [1]
            if block == [0, 0]:
                qr_block[j//2].append(full_block)
            elif block == [1, 0]:
                qr_block[j//2].append(down_half)
            elif block == [0, 1]:
                qr_block[j//2].append(up_half)
            elif block == [1, 1]:
                qr_block[j//2].append(blank)

    for row in qr_block:
        for e in row:
            print(e, end='')
        print()

itchat.utils.print_cmd_qr = print_cmd_qr

itchat.log.set_logging(loggingLevel=logging.INFO)

print(CQR)
itchat.auto_login(enableCmdQR=2, hotReload=True)
print(CEND)

friends = itchat.get_friends()
groups = itchat.get_chatrooms()
key = 0
contacts = dict()
key_table = dict()
for friend in friends:
    key_table[friend['UserName']] = key
    contacts[key] = {'NickName': friend['NickName'], 'UserName': friend['UserName']}
    key += 1
for group in groups:
    key_table[group['UserName']] = key
    contacts[key] = {'NickName': group['NickName'], 'UserName': group['UserName']}
    key += 1

@itchat.msg_register(itchat.content.INCOME_MSG, isGroupChat=True)
def group_print(msg):
    try:
        print(CGROUP + msg['User']['NickName'] + '--' + msg['ActualNickName']
                + ' #'+ '{}'.format(key_table[msg['User']['UserName']]) + '>>' + msg.text + CEND)
    except:
        try:
            print(CGROUP + '(' + msg['User']['NickName'] + '--' + msg['ActualNickName']
                    + ' #'+ '{}'.format(key_table[msg['User']['UserName']])
                    + msg['Type'] + ')' + CEND)
            if msg['MsgType'] == 3:
                with open('tmp.png', 'wb') as f:
                    f.write(msg['Text']())
                forward()
            if msg['MsgType'] == 62:
                with open('./mov/%s.mov' % datetime.now().timestamp(), 'wb') as f:
                    f.write(msg['Text']())
            if msg['MsgType'] == 34:
                with open('./wav/%s.wav' % datetime.now().timestamp(), 'wb') as f:
                    f.write(msg['Text']())
        except:
            print(sys.exc_info()[0])

@itchat.msg_register(itchat.content.INCOME_MSG, isFriendChat=True)
def friend_print(msg):
    try:
        print(CFRIEND + msg['User']['NickName'] + ' #' + '{}'.format(key_table[msg['User']['UserName']]) + '>>' + msg.text + CEND)
    except:
        try:
            print(CFRIEND + '(' + msg['User']['NickName']
                    + ' #{} '.format(key_table[msg['User']['UserName']])
                    + msg['Type'] + ')' + CEND)
            if msg['MsgType'] == 3:
                with open('tmp.png', 'wb') as f:
                    f.write(msg['Text']())
                forward()
            if msg['MsgType'] == 62:
                with open('./mov/%s.mov' % datetime.now().timestamp(), 'wb') as f:
                    f.write(msg['Text']())
            if msg['MsgType'] == 34:
                with open('./wav/%s.wav' % datetime.now().timestamp(), 'wb') as f:
                    f.write(msg['Text']())
        except:
            print(sys.exc_info()[0])

def print_members(userName):
    try:
        members = itchat.update_chatroom(userName=userName)['MemberList']
    except:
        return False
    for member in members:
        print(member['NickName'])
    print('{} members'.format(len(members)))
    return True

def forward():
    with open('slack.token', 'r') as f:
        param = json.load(f)
    files = {'file': open('tmp.png', 'rb')}
    print(requests.post(url='https://slack.com/api/files.upload', params=param, files=files))

class MsgCli(code.InteractiveConsole):
    ps_contact = '<<'
    ps_command = 'WeChat>>'
    ps_confirm = 'Send?[Y/n]>'
    def __init__(self, local=None, filename='<console>', hisfile=os.path.expanduser('~/.we_cli_his')):
        super().__init__(local, filename)

        colorama.init()
        self.status = 'command'

        itchat.run(blockThread=False)

    def print_help(self):
        if self.status == 'command':
            print(r'\l: list all')
            print(r'\g [id]: go into room id')
            print(r'\q: quit')
            print(r'\m: show all room members(only in room)')
            print(r'\img [file path]: send image(only in chat)')
        if self.status == 'incontact':
            print(r'\q: quit')
            print(r'\m: show all room members')
            print(r'\img [file path]: send image')

    def push(self, line):
        if self.status == 'command':
            sys.ps1 = self.ps_command
            if line == r'\l':
                for key, contact in contacts.items():
                    print(key, contact['NickName'])
            elif re.search(r'^\\g', line):
                try:
                    key = int(line[3:])
                except:
                    self.print_help()
                else:
                    if key >= 0 and key < len(contacts):
                        self.contact = contacts[key]
                        self.ps_contact = self.contact['NickName'] + '<<'
                        sys.ps1 = self.ps_contact
                        self.status = 'incontact'
            elif line == r'\h' or line != '':
                self.print_help()
        elif self.status == 'incontact':
            if line == r'\q':
                sys.ps1 = self.ps_command
                self.status = 'command'
            elif re.search(r'^\\img', line):
                self.img_path = line[5:]
                sys.ps1 = self.ps_confirm
                self.status = 'img_confirm'
            elif line == r'\m':
                print_members(self.contact['UserName'])
            elif line == r'\h':
                self.print_help()
            elif line != '':
                self.msg = line
                sys.ps1 = self.ps_confirm
                self.status = 'msg_confirm'
        elif self.status == 'img_confirm':
            if line == 'n':
                print(CRED + 'Cancelled.' + CEND)
            else:
                if itchat.send_image(self.img_path, toUserName=self.contact['UserName']):
                    print(CGREEN + 'Image sent!' + CEND)
                else:
                    print(CRED + 'Failed.' + CEND)
            sys.ps1 = self.ps_contact
            self.status = 'incontact'
        elif self.status == 'msg_confirm':
            if line in 'yY':
                try:
                    print(CGREEN + itchat.send_msg(msg=self.msg, toUserName=self.contact['UserName'])['BaseResponse']['RawMsg'] + CEND)
                except:
                    print(CRED + 'Failed.' + CEND)
            else:
                print(CYELLOW + 'Cancelled.' + CEND)
            sys.ps1 = self.ps_contact
            self.status = 'incontact'

def main():
    msg_cli = MsgCli()
    sys.ps1 = MsgCli.ps_command
    print('Welcome to Cli WeChat!')
    msg_cli.interact(r'Type \h for help')

if __name__ == '__main__':
    main()

