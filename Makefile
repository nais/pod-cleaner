image=docker.pkg.github.com/nais/pod-cleaner/pod-cleaner:0.4

build:
	docker build -t ${image} .

push:
	docker push ${image}
