image=ghcr.io/nais/pod-cleaner/pod-cleaner:1.0

.PHONY: install
install:
	python3 -m venv venv
	. venv/bin/activate; pip install flake8 pytest
	. venv/bin/activate; pip install -r requirements.txt

.PHONY: lint
lint:
	. venv/bin/activate; flake8 *.py --count --select=E9,F63,F7,F82 --show-source --statistics
	. venv/bin/activate; flake8 *.py --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

.PHONY: test
test:
	. venv/bin/activate; pytest *_test.py

.PHONY: e2e
e2e:
	. venv/bin/activate; python -m cleanup_e2e

.PHONY: build
build:
	docker build -t ${image} .

.PHONY: push
push:
	docker push ${image}
