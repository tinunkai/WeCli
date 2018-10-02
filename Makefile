all: run

deploy:
	rm -rf dist build *.egg-info
	pip install --upgrade setuptools wheel twine
	./setup.py sdist bdist_wheel
	twine upload dist/*

test:
	rm -rf dist build *.egg-info
	pip install --upgrade setuptools wheel twine
	./setup.py sdist bdist_wheel
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

run:
	./.wecli/bin/python wecli.py

install:
	./.wecli/bin/pip install -r requirements.txt

init:
	python3 -m venv .wecli
