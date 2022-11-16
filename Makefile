image=docker.pkg.github.com/nais/pod-cleaner/pod-cleaner:1.0

.PHONY: install
install:
	python3 -m venv venv
	pip install flake8 pytest
	. venv/bin/activate; pip install -r requirements.txt

.PHONY: test
test:
	. venv/bin/activate; python -m cleanup_test

.PHONY: build
build:
	docker build -t ${image} .

.PHONY: push
push:
	docker push ${image}
