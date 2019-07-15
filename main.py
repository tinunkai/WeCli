import sys,os
import curses
import time

import itchat
import colorful

def friend_register(stdscr):
    @itchat.msg_register(itchat.content.INCOME_MSG, isFriendChat=True)
    def _friend_register(msg):
        time.sleep(1)
        stdscr.addstr(0, 0, msg.text)
        stdscr.refresh()

def draw_menu(stdscr):
    friend_register(stdscr)
    itchat.run(blockThread=False)
    stdscr.addstr(1, 0, 'Hello')
    stdscr.refresh()
    k = stdscr.getch()

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
