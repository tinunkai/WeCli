.PHONY: install init history main
all: main

install:
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

oldinstall:
	.venv/bin/pip install -r wecli.requirements.txt

init:
	python -m venv .venv
	mkdir -p msgs

history:
	@.venv/bin/python history.py >> history &

main:
	@.venv/bin/python main.py

cli:
	@.venv/bin/python wecli.py
