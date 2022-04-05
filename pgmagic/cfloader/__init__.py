import enum
import logging
from os import getenv, environ
from threading import local

from sqlalchemy.pool import (NullPool,
                             QueuePool,
                             SingletonThreadPool,
                             StaticPool, )

from pgmagic.configurator import Config


class PoolMapping(enum.Enum):
    """
    Enum for pool mapping.
    """

    # A pool that uses the same connection for all requests
    # and that maintains one connection per thread.
    # It maintains one connection per each thread, never moving a connection
    # to a thread other than the one which it was created in.
    NullPool = {"engine": NullPool, "options": {}}

    # A Pool of exactly one connection, used for all requests.
    # Reconnect-related functions such as recycle and connection invalidation
    # (which is also used to support auto-reconnect) are only partially
    # supported right now and may not yield good results.
    StaticPool = {"engine": StaticPool, "options": {
        "pool_recycle": 900,
        "pool_size": 5,
        "max_overflow": 10
    }}

    # A Pool that imposes a limit on the number of open connections.
    # This is the default pool.
    QueuePool = {"engine": QueuePool, "options": {
        "pool_recycle": 900,
        "pool_size": 5,
        "max_overflow": 10
    }}

    # A Pool that maintains one connection per thread.
    # Maintains one connection per each thread, never moving a connection
    # to a thread other than the one which it was created in.
    SingletonThreadPool = {"engine": SingletonThreadPool, "options": {
        "pool_recycle": 900,
        "pool_size": 5,
        "max_overflow": 10
    }}


class Postgres(metaclass=Config):
    DATABASE = None

    CONNECTION_TIMEOUT = getenv("PGM_CONNECTION_TIMEOUT", 5)
    SSL_MODE = getenv("PGM_SSL_MODE")
    POOL = getenv("PGM_POOL", PoolMapping.NullPool.value)
    RO_RECONNECTS = getenv("PGM_RECONNECTS", 3)
    DELIMITER = getenv("PGM_DELIMITER", "_")

    PARAMS_DEFAULTS = {
        "PASSWORD": "postgres",
        "USER": "postgres",
        "DB": "postgres",
        "HOST": "postgres",
        "PORT": 5432,
        "SCHEME": "postgresql",
    }

    BASE = {}
    ENGINE = {}
    SESSION = {}
    ENV_PARAMS = {}
    SCOPED_SESSION = {}
    SESSION_CONTAINER = local()
    TPL = getenv("PGM_TPL", "{SCHEME}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}")
    if SSL_MODE:
      TPL += f"?sslmode={SSL_MODE}"
    RELOAD = False

    def connection_string(self, database):
        """
        Returns loaded params
        """
        self.load_params()

        if not self.ENV_PARAMS:
            return self.TPL.format(**self.PARAMS_DEFAULTS)

        if database not in self.ENV_PARAMS:
            logging.error(f"{database} NOT FOUND IN PARAMETERS!")
            return ""

        return self.TPL.format(**self.ENV_PARAMS.get(database))

    def load_params(self):
        """
        Loads params from environment variables
        """
        params = {}

        for key in environ.keys():

            if key.startswith(getenv("PGM_PREFIX", "PG")):
                value = getenv(key)

                try:
                    prefix, parameter, postfix = key.split(self.DELIMITER, 3)
                except ValueError:
                    postfix = "default"
                    prefix, parameter = key.split(self.DELIMITER, 2)

                if postfix not in params:
                    params[postfix] = {}

                params[postfix][parameter] = value

        for key in params.keys():
            params[key] = {**self.PARAMS_DEFAULTS, **params[key]}

        self.ENV_PARAMS = params


def pg_cfg(database):
    return Postgres().connection_string(database)


if __name__ == "__main__":
    print(pg_cfg("default"))
