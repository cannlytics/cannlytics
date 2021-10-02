all:
	run

npm_image:
	docker build -t npm-image -f Dockerfile-node .

build:
	docker build -t cannlytics -f Dockerfile .

npm:
	docker run --rm -it \
	--name npm \
    -p 8090:8080 \
    -p 8000:8000 \
    -p 8081:8081 \
    -p 35729:35729 \
	-v `pwd`:/app \
	-w /app \
	npm-image $(c)


install: npm_image node_modules

install_firebase_tools:
	make npm c="npm install -g firebase-tools"

install_webpack:
	make npm c="npm install webpack-dev-server --save-dev"

webpack-dev:
	make npm c="webpack-dev-server --env production=False"

.PHONY: node_modules
node_modules:
	make npm c="npm install"

live:
	make npm c="npm start"

update:
	make npm c="npm update"

audit-fix:
	make npm c="npm audit fix"

docker.env:
	cp .env docker.env

.env:
	cp .env.example .env
	sed -i '/SECRET_KEY/d' .env
	docker run --rm -it \
	-v `pwd`/django_secret.py:/app/django_secret.py \
	cannlytics-back \
	python -c "from django.utils.crypto import get_random_string;print(get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789\!\@\#$%^&*(-_=+)'))" > sk
	@echo SECRET_KEY=$$(cat sk) >> .env
	@rm sk
	@echo "Minimal .env file created"
