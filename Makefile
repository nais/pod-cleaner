image=ghcr.io/nais/pod-cleaner/pod-cleaner:1.0

build:
	docker build -t ${image} .

push:
	docker push ${image}
