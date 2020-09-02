image=docker.pkg.github.com/nais/pod-cleaner/pod-cleaner:1.0

build:
	docker build -t ${image} .

push:
	docker push ${image}
