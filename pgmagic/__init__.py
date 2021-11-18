import logging
from contextlib import contextmanager
from time import sleep

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import psycopg2
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from pgmagic.cfloader import pg_cfg, Postgres
from pgmagic.connectors.logging import LoggingConnection

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def is_ro(cur):
    cur.execute("SELECT pg_is_in_recovery()")
    result = cur.fetchone()
    return bool(result) and result[0]


def __conn_factory(*args, **kwargs):
    for _ in range(Postgres.RO_RECONNECTS):
        connection = LoggingConnection(*args, **kwargs)
        connection.autocommit = False

        if is_ro(connection.cursor()):
            logger.warning('Database is read-only, reconnecting')
            connection.close()
            sleep(1)
            continue
        return connection

    raise psycopg2._psycopg.OperationalError('Database is read-only')


def get_engine(database="default"):
    return create_engine(
        pg_cfg(database),
        connect_args={
            "connect_timeout": Postgres.CONNECTION_TIMEOUT,
            "connection_factory": __conn_factory,
        },
        poolclass=Postgres.POOL.get("engine"),
        **Postgres.POOL.get("options")
    )


def get_base(database="default"):
    if not Postgres.BASE.get(database):
        init(database)
    return Postgres.BASE.get(database)


def init(database="default"):
    Postgres.SESSION[database] = sessionmaker(
        bind=get_engine(database),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False, )

    Postgres.ENGINE[database] = get_engine(database)
    Postgres.SESSION.get(database).configure(bind=Postgres.ENGINE.get(database))
    Postgres.SCOPED_SESSION[database] = scoped_session(Postgres.SESSION.get(database))
    Postgres.BASE[database] = declarative_base()
    Postgres.BASE.get(database).query = Postgres.SCOPED_SESSION.get(database).query_property()


@contextmanager
def session(session_name="default"):
    if not Postgres.ENGINE.get(session_name):
        init(session_name)

    _engine = Postgres.ENGINE.get(session_name)
    _session = Postgres.SESSION.get(session_name)()
    _scoped_session = Postgres.SCOPED_SESSION.get(session_name)

    nested_session = False

    if hasattr(Postgres.SESSION_CONTAINER, f"session_{session_name}"):
        new_session = getattr(Postgres.SESSION_CONTAINER, f"session_{session_name}")
        nested_session = True
    else:
        new_session = _scoped_session
        setattr(Postgres.SESSION_CONTAINER, f"session_{session_name}", new_session)

    try:
        yield new_session
        if not nested_session:
            invalidated = any(
                isinstance(c, _engine.base.Connection) and c.invalidated for c in _session.transaction._connections
            )
            if not invalidated:
                new_session.commit()
            else:
                try:
                    new_session.rollback()
                except BaseException as e:
                    logging.info(str(e))
    except BaseException:
        new_session.rollback()
        raise
    finally:
        if not nested_session:
            new_session.close()
            _scoped_session.remove()
            delattr(Postgres.SESSION_CONTAINER, f"session_{session_name}")
