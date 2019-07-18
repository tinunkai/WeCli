import sys, os, tempfile
import curses
import curses.ascii
from curses.textpad import Textbox
import time
import json
import requests
from datetime import datetime
from subprocess import call

import itchat
from itchat.content import *
import colorful

from utils import print_cmd_qr

class WeCli:
    def __init__(self, stdscr):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        self.stdscr = stdscr
        self.moment = datetime.now()
        self.linetop = 0
        self.select_top = self.select_line = 0
        self.status = ''
        self.msg_send = ''
        self.editor = os.environ.get('EDITOR', 'vim')
        self.nick = self.user = 'WeCli'
        if not os.path.exists(self.msgs_path()):
            with open(self.msgs_path(), 'w'): pass
        with open(self.msgs_path(), 'r') as f:
            self.msgs = f.read().strip().split('\n')
        self.make_wins()
        self.text_register()
        self.media_register()
        self.refresh()

    def msgs_path(self):
        return 'msgs/%s.msg' % self.moment.strftime('%Y%m%d')

    def __call__(self):
        self.k = None
        while True:
            self.k = self.stdscr.getch()
            if self.k == ord('q'):
                if self.user != 'WeCli':
                    self.nick = self.user = 'WeCli'
                else:
                    break
            if self.k == curses.ascii.ctrl(ord('l')):
                self.status = ''
                self.msg_win.clear()
                self.refresh()
            elif self.k == curses.ascii.ctrl(ord('d')):
                if self.linetop == len(self.msgs) - 1: continue
                self.linetop += self.msg_height // 2
                if self.linetop > len(self.msgs) - 1:
                    self.linetop = len(self.msgs) - 1
                self.draw_msg()
            elif self.k == curses.ascii.ctrl(ord('u')):
                if self.linetop == 0: continue
                self.linetop -= self.msg_height // 2
                if self.linetop < 0:
                    self.linetop = 0
                self.draw_msg()
            elif self.k == ord('j'):
                if self.linetop == len(self.msgs) - 1: continue
                self.linetop += 1
                if self.linetop > len(self.msgs) - 1:
                    self.linetop = len(self.msgs) - 1
                self.draw_msg()
            elif self.k == ord('k'):
                if self.linetop == 0: continue
                self.linetop -= 1
                if self.linetop < 0:
                    self.linetop = 0
                self.draw_msg()
            elif self.k == ord('g'):
                self.linetop = 0
                self.draw_msg()
            elif self.k == ord('G'):
                self.linetop = len(self.msgs) - 1
                self.draw_msg()
            elif self.k in (ord(':'), ord('r'), ord('m')):
                self.select_contact(self.k)
            elif self.k == ord('i'):
                if self.user != 'WeCli':
                    self.get_input()
            elif self.k == ord('e'):
                call([self.editor, 'main.py'])
            elif self.k == curses.KEY_RESIZE:
                self.make_wins()
            self.refresh()

    def get_input(self):
        self.status = '<<'
        self.draw_status()
        call([self.editor, '.tmp'])
        with open('.tmp', 'r') as tf:
            self.msg_send = tf.read()
        self.refresh()
        self.send_msg()

    def send_msg(self):
        self.status='<<send?(y/n)'
        self.draw_status(clear=False)
        while True:
            self.k = self.stdscr.getch()
            if self.k == ord('y'):
                self.response = itchat.send_msg(
                        msg=self.msg_send, toUserName=self.user)['BaseResponse']['RawMsg']
                self.status = '>' + self.response
                line = '%s @ %s < %s' % (self.nick, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.msg_send)
                with open(self.msgs_path(), 'a') as f:
                    f.write(line)
                self.msgs.append(line.strip())
                break
            if self.k == ord('n'):
                self.status = '<canceled'
                break
        self.draw_status()

    def draw_status(self, clear=True):
        if clear:
            self.input_win.clear()
        self.input_win.addstr(0, 0, '--')
        self.input_win.addstr(1, 0, self.nick + self.status, curses.color_pair(1))
        self.input_win.refresh()

    def select_contact(self, key):
        self.select_line = self.select_top = 0
        self.msg_win.clear()
        self.contacts = list()
        friends = itchat.get_friends()
        groups = itchat.get_chatrooms()
        if key in (ord(':'), ord('m')):
            for friend in friends:
                self.contacts.append((friend['NickName'], friend['UserName']))
        if key in (ord(':'), ord('r')):
            for group in groups:
                self.contacts.append((group['NickName'], group['UserName']))

        self.draw_select()
        while True:
            self.k = self.stdscr.getch()
            if self.k == ord('q'):
                break
            elif self.k == ord('j'):
                if self.select_line < len(self.contacts) - 1:
                    self.select_line += 1
                if self.select_line - self.select_top >= self.ym - self.input_height:
                    self.select_top += 1
                    self.msg_win.clear()
                self.draw_select()
            elif self.k == ord('k'):
                if self.select_line > 0:
                    self.select_line -= 1
                if self.select_line < self.select_top:
                    self.select_top -= 1
                    self.msg_win.clear()
                self.draw_select()
            elif self.k == curses.ascii.ctrl(ord('d')):
                self.select_line += self.msg_height // 2
                self.select_top += self.msg_height // 2
                if self.select_line > len(self.contacts) - 1:
                    self.select_line = len(self.contacts) - 1
                if self.select_top > len(self.contacts) - 1:
                    self.select_top = len(self.contacts) - 1
                self.msg_win.clear()
                self.draw_select()
            elif self.k == curses.ascii.ctrl(ord('u')):
                self.select_line -= self.msg_height // 2
                self.select_top -= self.msg_height // 2
                if self.select_line < 0:
                    self.select_line = 0
                if self.select_top < 0:
                    self.select_top = 0
                self.msg_win.clear()
                self.draw_select()
            elif self.k == ord('g'):
                self.select_line = 0
                self.select_top = 0
                self.msg_win.clear()
                self.draw_select()
            elif self.k == ord('G'):
                self.select_line = len(self.contacts) - 1
                self.select_top = len(self.contacts) - 1
                self.msg_win.clear()
                self.draw_select()
            elif self.k == 10:
                self.nick, self.user = self.contacts[self.select_line]
                self.draw_status()
                break
            elif self.k == curses.ascii.ctrl(ord('l')):
                self.msg_win.clear()
                self.draw_select()
            elif self.k == curses.ascii.ctrl(ord('l')):
                self.msg_win.clear()
                self.draw_select()
        self.msg_win.clear()

    def draw_select(self):
        select_nick, select_user = self.contacts[self.select_line]
        for y, (nick, user) in enumerate(self.contacts
                [self.select_top:self.select_top + self.ym - self.input_height]):
            if user == select_user:
                nick = '>>> ' + nick
                self.msg_win.addstr(y, 0, nick, curses.color_pair(1))
            else:
                nick = '    ' + nick
                self.msg_win.addstr(y, 0, nick)
        self.msg_win.refresh()

    def text_register(self):
        @itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING],
                isFriendChat=True, isGroupChat=True, isMpChat=True)
        def _text_register(msg):
            try:
                name = msg['User']['NickName']
            except KeyError:
                name = msg['User']['UserName']
            if 'ActualNickName' in msg:
                line = '%s >> %s @ %s > %s\n' % (
                        name, msg['ActualNickName'],
                        datetime.fromtimestamp(msg['CreateTime']), msg.text)
            else:
                line = '%s @ %s > %s\n' % (
                        name, datetime.fromtimestamp(msg['CreateTime']), msg.text)
            with open(self.msgs_path(), 'a') as f:
                f.write(line)
            self.msgs.append(line.strip())
            self.draw_msg()

    def media_register(self):
        @itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO],
                isFriendChat=True, isGroupChat=True, isMpChat=True)
        def _media_register(msg):
            try:
                name = msg['User']['NickName']
            except KeyError:
                name = msg['User']['UserName']
            if 'ActualNickName' in msg:
                line = '%s >> %s @ %s > %s\n' % (
                        name, msg['ActualNickName'],
                        datetime.fromtimestamp(msg['CreateTime']), msg.fileName)
            else:
                line = '%s @ %s > %s\n' % (
                        name, datetime.fromtimestamp(msg['CreateTime']), msg.fileName)
            self.msgs.append(line)
            with open(self.msgs_path(), 'a') as f:
                f.write(line)
            #with open('slack.token.json', 'r') as f:
            #    param = json.load(f)
            #files = {'file': msg.download(None)}
            #requests.post(url='https://slack.com/api/files.upload', params=param, files=files)
            self.msg_win.refresh()

    def refresh(self):
        self.draw_msg()
        self.draw_status()

    def draw_msg(self):
        self.msg_win.clear()
        lp = 0
        for line in self.msgs[self.linetop:]:
            lh = 2 * len(line) // self.xm + 1
            if lp + lh >= self.msg_height:
                break
            if '>>' in line:
                self.msg_win.addstr(lp, 0, line, curses.color_pair(2))
            elif '>' in line:
                self.msg_win.addstr(lp, 0, line, curses.color_pair(3))
            else:
                self.msg_win.addstr(lp, 0, line)
            lp = self.msg_win.getyx()[0] + 1
        self.msg_win.refresh()

    def make_wins(self):
        self.input_height = 2
        self.ym, self.xm = self.stdscr.getmaxyx()
        self.msg_height = self.ym - self.input_height
        self.stdscr.erase()
        self.msg_win = self.stdscr.subwin(self.msg_height, self.xm, 0, 0)
        self.input_win = self.stdscr.subwin(self.input_height, self.xm, self.msg_height, 0)

def draw_menu(stdscr):
    wecli = WeCli(stdscr)
    itchat.run(blockThread=False)
    wecli()

def main():
    itchat.utils.print_cmd_qr = print_cmd_qr
    itchat.auto_login(enableCmdQR=2, hotReload=True)
    curses.wrapper(draw_menu)

def validator(ch):
    return ch

if __name__ == "__main__":
    main()
