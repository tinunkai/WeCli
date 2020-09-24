.PHONY: install init history main
all: try

install:
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

oldinstall:
	.venv/bin/pip install -r wecli.requirements.txt

init:
	python -m venv .venv
	mkdir -p msgs
	mkdir -p media

history:
	@.venv/bin/python history.py >> history &

main:
	@.venv/bin/python main.py

try:
	@.venv/bin/python try.py

cli:
	@.venv/bin/python wecli.py
