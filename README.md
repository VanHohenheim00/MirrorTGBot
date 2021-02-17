.env file


TELEGRAM_BOT_TOKEN=<br>
ETHPLORER_API_KEY=<br>
POSTGRES_USER=postgres<br>
POSTGRES_PASSWORD=<br>
POSTGRES_HOST=db<br>
POSTGRES_PORT=5432<br>
POSTGRES_DB=postgres<br>

commands to init db:

docker-compose exec bot aerich init -t models.db.TORTOISE_ORM<br>
docker-compose exec bot aerich init-db

commands to migrate:

docker-compose exec bot aerich migrate<br>
docker-compose exec bot aerich upgrade