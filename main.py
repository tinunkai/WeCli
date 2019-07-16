import sys,os
import curses
import curses.ascii
from curses.textpad import Textbox
import time
import json
import requests
from datetime import datetime
import unicodedata

import itchat
from itchat.content import *
import colorful

def isunicode(c):
    return unicodedata.category(chr(c))[0] in 'LNPS'

curses.ascii.isprint = isunicode

class WeCli:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.moment = datetime.now()
        self.linetop = 0
        self.nick, self.user = 'None', 'None'
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
                break
            if self.k == curses.ascii.ctrl(ord('l')):
                self.msg_win.clear()
                self.refresh()
            elif self.k == curses.ascii.ctrl(ord('d')):
                self.linetop += self.ym // 2
                if self.linetop > len(self.msgs) - 1:
                    self.linetop = len(self.msgs) - 1
                self.draw_msg()
            elif self.k == curses.ascii.ctrl(ord('u')):
                self.linetop -= self.ym // 2
                if self.linetop < 0:
                    self.linetop = 0
                self.draw_msg()
            elif self.k == ord('j'):
                self.linetop += 1
                if self.linetop > len(self.msgs) - 1:
                    self.linetop = len(self.msgs) - 1
                self.draw_msg()
            elif self.k == ord('k'):
                self.linetop -= 1
                if self.linetop < 0:
                    self.linetop = 0
                self.draw_msg()
            elif self.k == ord('g'):
                self.linetop = 0
                self.draw_msg()
            elif self.k == ord('G'):
                self.linetop = len(self.msgs) - self.ym + 1
                self.draw_msg()
            elif self.k == ord(':'):
                self.select_contact()
            elif self.k == ord('i'):
                self.draw_status()
            elif self.k == curses.KEY_RESIZE:
                self.make_wins()
            self.refresh()

    def draw_status(self):
        self.command_win.clear()
        self.command_win.addstr(0, self.xm - 2*len(self.nick) - 1, self.nick)
        self.command_win.move(0, 0)
        self.command_win.refresh()

    def select_contact(self):
        self.msg_win.clear()
        self.contacts = list()
        friends = itchat.get_friends()
        groups = itchat.get_chatrooms()
        for friend in friends:
            self.contacts.append((friend['NickName'], friend['UserName']))
        for group in groups:
            self.contacts.append((group['NickName'], group['UserName']))

        self.select_top = self.select_line = 0
        self.draw_select()
        while True:
            self.k = self.stdscr.getch()
            if self.k == ord('q'):
                break
            elif self.k == ord('j'):
                if self.select_line < len(self.contacts) - 1:
                    self.select_line += 1
                if self.select_line - self.select_top >= self.ym - 1:
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
            elif self.k == 10:
                self.nick, self.user = self.contacts[self.select_line]
                self.draw_status()
                break
            elif self.k == curses.ascii.ctrl(ord('l')):
                self.msg_win.clear()
                self.draw_select()
        self.msg_win.clear()

    def draw_select(self):
        select_nick, select_user = self.contacts[self.select_line]
        for y, (nick, user) in enumerate(self.contacts
                [self.select_top:self.select_top + self.ym - 1]):
            if user == select_user:
                nick = '>>> ' + nick
            else:
                nick = '    ' + nick
            self.msg_win.addstr(y, 0, nick)
        self.msg_win.refresh()

    def text_register(self):
        @itchat.msg_register(TEXT)
        def _text_register(msg):
            try:
                name = msg['User']['NickName']
            except KeyError:
                name = msg['User']['UserName']
            line = '%s @ %s > %s\n' % (
                    name,
                    datetime.fromtimestamp(msg['CreateTime']),
                    msg.text)
            with open(self.msgs_path(), 'a') as f:
                f.write(line)
            self.msgs.append(line)
            self.draw_msg()

    def media_register(self):
        @itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
        def _media_register(msg):
            with open('slack.token.json', 'r') as f:
                param = json.load(f)
            files = {'file': msg.download(None)}
            with open(self.msgs_path(), 'a') as f:
                f.write(msg.fileName)

            try:
                name = msg['User']['NickName']
            except KeyError:
                name = msg['User']['UserName']
            line = '%s @ %s > %s\n' % (
                    name, datetime.fromtimestamp(msg['CreateTime']), msg.fileName)
            self.msgs.append(line)
            requests.post(url='https://slack.com/api/files.upload', params=param, files=files)
            self.msg_win.refresh()

    def refresh(self):
        self.draw_msg()
        self.command_win.refresh()

    def draw_msg(self):
        self.msg_win.clear()
        lp = 0
        for line in self.msgs[::-1][self.linetop:]:
            lh = len(line) // self.xm + 1
            if lp + lh >= self.ym - 1:
                break
            self.msg_win.addstr(lp, 0, line)
            lp += lh
        self.msg_win.refresh()

    def make_wins(self):
        self.stdscr.erase()
        self.ym, self.xm = self.stdscr.getmaxyx()
        self.msg_win = self.stdscr.subwin(self.ym - 1, self.xm, 0, 0)
        self.command_win = self.stdscr.subwin(1, self.xm, self.ym - 1, 0)

def draw_menu(stdscr):
    wecli = WeCli(stdscr)
    itchat.run(blockThread=False)
    wecli()

def main():
    itchat.utils.print_cmd_qr = print_cmd_qr
    itchat.auto_login(enableCmdQR=2, hotReload=True)
    curses.wrapper(draw_menu)

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

def validator(ch):
    return ch

if __name__ == "__main__":
    main()
