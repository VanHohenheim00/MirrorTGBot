start:
	docker-compose up  --remove-orphans

start_daemon:
	docker-compose up -d --remove-orphans

build:
	docker-compose build --no-cache

stop:
	docker-compose down

restart:
	stop
	start