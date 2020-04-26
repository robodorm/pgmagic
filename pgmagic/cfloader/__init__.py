import enum
from os import getenv, environ
from threading import local

from sqlalchemy.pool import (NullPool,
                             QueuePool,
                             SingletonThreadPool,
                             StaticPool, )

from pgmagic.configurator import Config, provide_config


class Postgres(metaclass=Config):
    class PoolMapping(enum.Enum):
        NullPool = {"engine": NullPool, "options": {
        }}

        StaticPool = {"engine": StaticPool, "options": {
            "pool_recycle": 900,
            "pool_size": 5,
            "max_overflow": 10
        }}

        QueuePool = {"engine": QueuePool, "options": {
            "pool_recycle": 900,
            "pool_size": 5,
            "max_overflow": 10
        }}

        SingletonThreadPool = {"engine": SingletonThreadPool, "options": {
            "pool_recycle": 900,
            "pool_size": 5,
            "max_overflow": 10
        }}

    DATABASE = None
    PREFIX = getenv("PGM_PREFIX", "PG")
    CONNECTION_TIMEOUT = getenv("PGM_CONNECTION_TIMEOUT", 5)
    POOL = getenv("PGM_POOL", PoolMapping.NullPool.value)
    RO_RECONNECTS = getenv("PGM_RECONNECTS", 3)
    DELIMITER = getenv("PGM_DELIMITER", "_")

    PARAMS_DEFAULTS = {
        "PASSWORD": "postgres",
        "USER": "postgres",
        "DB": "postgres",
        "HOST": "postgres",
        "PORT": 5432
    }

    BASE = {}
    ENGINE = {}
    SESSION = {}
    ENV_PARAMS = {}
    SCOPED_SESSION = {}
    SESSION_CONTAINER = local()
    TPL = getenv("PGM_TPL", "postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}")


def load_params():
    params = {}

    for key in environ.keys():

        if key.startswith(Postgres.PREFIX):
            value = getenv(key)

            try:
                prefix, parameter, postfix = key.split(Postgres.DELIMITER, 3)
            except ValueError:
                postfix = "default"
                prefix, parameter = key.split(Postgres.DELIMITER, 2)

            if postfix not in params:
                params[postfix] = {}

            params[postfix][parameter] = value

    for key in params.keys():
        params[key] = {**params[key], **Postgres.PARAMS_DEFAULTS}

    Postgres.ENV_PARAMS = params


@provide_config(Postgres)
def pg_cfg(database, cfg):

    if not cfg.ENV_PARAMS:
        load_params()

    return cfg.TPL.format(**cfg.ENV_PARAMS.get(database))


if __name__ == "__main__":
    print(pg_cfg("default"))
