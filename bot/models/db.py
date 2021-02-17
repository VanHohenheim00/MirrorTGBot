from tortoise import Tortoise
import os

TORTOISE_ORM = {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": os.environ["POSTGRES_HOST"],
                        "port": os.environ["POSTGRES_PORT"],
                        "user": os.environ["POSTGRES_USER"],
                        "password": os.environ["POSTGRES_PASSWORD"],
                        "database": os.environ["POSTGRES_DB"],
                    },
                }
            },
            "apps": {"models": {"models": ["models",  "aerich.models"], "default_connection": "default"}},
            "use_tz": False,
            "timezone": 'UTC'
        }

async def init():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(TORTOISE_ORM)
    #await Tortoise.generate_schemas()
    # Generate the schema