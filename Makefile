SHELL := /bin/bash

install:
	echo 'TODO'

install-dev:
	echo 'TODO'

rebuild-local-db:
	rm -f local.db
	alembic upgrade head

run:
	uvicorn src.app:app --port 8000 --reload

docker-login:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 122253718099.dkr.ecr.us-east-1.amazonaws.com

docker-build:
	docker build -t bottestai-backend:latest .

docker-tag:
	docker tag bottestai-backend:latest 122253718099.dkr.ecr.us-east-1.amazonaws.com/bottestai-backend:latest

docker-push:
	docker push 122253718099.dkr.ecr.us-east-1.amazonaws.com/bottestai-backend:latest

docker-deploy:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 122253718099.dkr.ecr.us-east-1.amazonaws.com
	docker build -t bottestai-backend:latest .
	docker tag bottestai-backend:latest 122253718099.dkr.ecr.us-east-1.amazonaws.com/bottestai-backend:latest
	docker push 122253718099.dkr.ecr.us-east-1.amazonaws.com/bottestai-backend:latest
