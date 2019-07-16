import sys,os
import curses
import curses.ascii
from curses.textpad import Textbox
import time
import json
import requests
from datetime import datetime

import itchat
from itchat.content import *
import colorful

class WeCli:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.moment = datetime.now()
        if not os.path.exists(self.msgs_path()):
            with open(self.msgs_path(), 'w'): pass
        with open(self.msgs_path(), 'r') as f:
            self.msgs = f.read()
        self.make_wins()
        self.text_register()
        self.media_register()

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
            elif self.k == ord('i'):
                pass
            elif self.k == ord(':'):
                self.command_win.addstr(0, 0, ':')
                self.command_box.edit()
                self.command = self.command_box.gather()
                self.command_win.clear()
            elif self.k == curses.KEY_RESIZE:
                self.make_wins()
            self.refresh()

    def text_register(self):
        @itchat.msg_register(TEXT)
        def _text_register(msg):
            line = '%s > %s\n' % (msg['User']['NickName'], msg.text)
            with open(self.msgs_path(), 'a') as f:
                f.write(line)
            self.msgs += line
            self.draw_msg()

    def media_register(self):
        @itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
        def _media_register(msg):
            with open('slack.token.json', 'r') as f:
                param = json.load(f)
            files = {'file': msg.download(None)}
            with open(self.msgs_path(), 'a') as f:
                f.write(msg.fileName)
            self.msgs += msg.fileName
            requests.post(url='https://slack.com/api/files.upload', params=param, files=files)
            self.msg_win.refresh()

    def refresh(self):
        self.draw_msg()
        self.command_win.refresh()

    def draw_msg(self):
        self.msg_win.addstr(0, 0, self.msgs)
        self.msg_win.refresh()

    def make_wins(self):
        self.stdscr.erase()
        self.ym, self.xm = self.stdscr.getmaxyx()
        self.msg_win = self.stdscr.subwin(self.ym - 1, self.xm, 0, 0)
        self.command_win = self.stdscr.subwin(1, self.xm, self.ym - 1, 0)
        self.command_box = Textbox(self.command_win)
        self.refresh()

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

if __name__ == "__main__":
    main()
