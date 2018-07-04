#!/usr/bin/env python3

import time
import threading
import sys
import logging
import code
import atexit
import os
import re
try:
    import readline
except:
    pass

import itchat
import colorama

CQR = colorama.Fore.WHITE + colorama.Back.BLACK
CFRIEND = colorama.Fore.MAGENTA
CGROUP = colorama.Fore.CYAN
CRED = colorama.Fore.RED
CYELLOW = colorama.Fore.YELLOW
CGREEN = colorama.Fore.GREEN
CEND = colorama.Style.RESET_ALL

itchat.log.set_logging(loggingLevel=logging.INFO)

@itchat.msg_register(itchat.content.INCOME_MSG, isGroupChat=True)
def group_print(msg):
    try:
        print(CGROUP + msg['User']['NickName'] + '--' + msg['ActualNickName'] + '=>' + msg.text + CEND)
    except:
        pass

@itchat.msg_register(itchat.content.INCOME_MSG, isFriendChat=True)
def friend_print(msg):
    try:
        print(CFRIEND + msg['User']['NickName'] + '=>' + msg.text + CEND)
    except:
        pass

def send_msg(msg, name):
    user_name = itchat.search_friends(nickName=name)[0]['UserName']
    return itchat.send_msg(msg=msg, toUserName=user_name)

def print_members(userName):
    try:
        members = itchat.update_chatroom(userName=userName)['MemberList']
    except:
        return False
    for member in members:
        print(member['NickName'])
    print('{} members'.format(len(members)))
    return True

class MsgCli(code.InteractiveConsole):
    ps_contact = '<='
    ps_command = 'WeChat>>'
    ps_confirm = 'Send?[Y/n]>'
    def __init__(self, local=None, filename='<console>', hisfile=os.path.expanduser('~/.we_cli_his')):
        super().__init__(local, filename)

        colorama.init()
        self.status = 'command'
        self.contacts = dict()

        print(CQR)
        itchat.auto_login(enableCmdQR=2, hotReload=True)
        print(CEND)
        itchat.run(blockThread=False)

        friends = itchat.get_friends()
        groups = itchat.get_chatrooms()
        key = 0
        for friend in friends:
            row = dict()
            row['NickName'] = friend['NickName']
            row['UserName'] = friend['UserName']
            self.contacts[key] = row
            key += 1
        for group in groups:
            row = dict()
            row['NickName'] = group['NickName']
            row['UserName'] = group['UserName']
            self.contacts[key] = row
            key += 1

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
                for key, contact in self.contacts.items():
                    print(key, contact['NickName'])
            elif re.search(r'^\\g', line):
                try:
                    key = int(line[3:])
                except:
                    self.print_help()
                else:
                    if key >= 0 and key < len(self.contacts):
                        self.contact = self.contacts[key]
                        self.ps_contact = self.contact['NickName'] + '<='
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

