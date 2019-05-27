all: run

deploy:
	rm -rf dist build *.egg-info
	pip install --upgrade setuptools wheel twine
	setup.py sdist bdist_wheel
	twine upload dist/*

test:
	rm -rf dist build *.egg-info
	pip install --upgrade setuptools wheel twine
	setup.py sdist bdist_wheel
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

run:
	.venv/bin/python wecli.py

install:
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

init: dir
	python -m venv .venv

dir:
	mkdir -p png wav mov

winstall:
	.venv\Scripts\pip install --upgrade pip
	.venv\Scripts\pip install -r requirements.txt

wrun:
	.venv\Scripts\python wecli.py
