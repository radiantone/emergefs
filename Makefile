.DEFAULT_GOAL := all
black = black --target-version py39 emerge
isort = isort --profile black emerge

.PHONY: depends
depends:
	bash ./bin/depends.sh

.PHONY: init
init: depends
	echo "Setting up virtual environment in venv/"
	python3 -m venv venv
	echo "Virtual environment complete."

.PHONY: format
format:
	$(isort)
	$(black)

.PHONY: lint
lint:
	mypy --show-error-codes  --ignore-missing-imports emerge
	flake8 --ignore=E203,F841,E501,E722,W503  emerge
	$(isort) --check-only --df
	$(black) --check --diff

.PHONY: setup
setup:
	python3 setup.py install

.PHONY: install
install: depends init
	. venv/bin/activate && ( \
	pip3 install -r requirements.txt; \
	python3 setup.py install; \
	python3 setup.py clean; \
	)

.PHONY: update
update: format lint
	pip3 freeze | grep -v emerge > requirements.txt
	git add setup.py docs bin emerge requirements.txt Makefile README.md scripts
	git commit --allow-empty -m "Updates"
	git push origin main
	python3 setup.py install
	git status

.PHONY: build
build:
	docker compose build

.PHONY: up
up: build
	docker compose up

.PHONY: down
down:
	docker compose stop

.PHONY: docs
docs:
	cd docs
	make -C docs html

.PHONY: clean
clean:
	rm -rf data/broker/*
	rm -rf data/node2/*
	python3 setup.py clean
	git status

.PHONY: tests
tests: format lint
	pytest emerge/tests
	
.PHONY: all
all: format lint update docs install tests clean
	git status
