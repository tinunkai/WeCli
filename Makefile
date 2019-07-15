all: main

main:
	.venv/bin/python main.py

install:
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

init:
	python -m venv .venv
