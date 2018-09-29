import enum
from os import getenv
from threading import local

from sqlalchemy.pool import (NullPool,
                             QueuePool,
                             SingletonThreadPool,
                             StaticPool, )

from pgmagic.configurator import Config, provide_config


class Postgres(Config):
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

    PREFIX = "PG"
    DATABASE = None
    CONNECTION_TIMEOUT = 5
    POOL = PoolMapping.NullPool.value
    RO_RECONNECTS = 3
    EXTRA = None
    DELIMITER = "_"
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
    SCOPED_SESSION = {}
    SESSION_CONTAINER = local()

    TPL = "postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"


@provide_config(Postgres)
def pg_cfg(cfg):
    params = {}
    for param, default in cfg.PARAMS_DEFAULTS.iteritems():

        postfix = ""

        if cfg.POSTFIX:
            postfix = f"{cfg.DELIMITER}{cfg.POSTFIX}"

        params[param] = getenv(f"{cfg.PREFIX}{cfg.DELIMITER}{param}{postfix}",
                               getenv(f"{cfg.PREFIX}{cfg.DELIMITER}{param}", default))

    return cfg.TPL.format(params)


if __name__ == "__main__":
    print(pg_cfg())
