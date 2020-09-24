# WeCli
Another terminal wechat inspired by [node-wechat-terminal][node-wechat-terminal]
and [itchat][itchat].

## Dependencies
- unix like operating system (or whatever supporting curses)
- [python3][python3]  
optional(for simple installing and running)
- [make][make]

## Install
```shell
make init
make install
```
for using wecli.py
```shell
make oldinstall
```

## Usage
curses UI wecli:
```shell
make main
```
vim-like key bind. j/k/C-u/C-d/g/G  
`:`: call select contact menu  
`m`: only search friends  
`r`: only search groups  
`i`: call system EDITOR for editing message (recommand neovim for unicode characters)

cli UI wecli:
```shell
make cli
```
wecli.py may run on Windows with the terminal supporting unicode  
`\h`: help message  
`\l`: list contacts with id numbers  
`\g [id]`: go into a contact  
`\q`: quit contact room
`\m`: in group chatroom, list room members

## New Features
- [x] new UI based on curses
- [x] slack forward
- [x] colored message
- [ ] send file
- [ ] PGP functions

[node-wechat-terminal]: https://github.com/goorockey/node-wechat-terminal
[itchat]: https://github.com/littlecodersh/ItChat
[python3]: https://www.python.org/
[make]: https://www.gnu.org/software/make/
