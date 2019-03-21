import logging
import psycopg2
import psycopg2.extensions
import psycopg2.extras

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

from pgmagic.cursors.logging import LoggingCursor


class LoggingConnection(psycopg2.extras.LoggingConnection):
    def __init__(self, *args, **kwargs):
        super(LoggingConnection, self).__init__(*args, **kwargs)
        self.initialize(logger)

    def cursor(self, *args, **kwargs):
        self._check()
        kwargs.setdefault('cursor_factory', LoggingCursor)
        return psycopg2.extensions.connection.cursor(self, *args, **kwargs)

    # It's not possible to log transaction begin here: as per DBAPI spec,
    # transaction is started implicitly with the first statement executed.

    def commit(self):
        do_log = self.get_transaction_status()
        super(LoggingConnection, self).commit()
        if do_log:
            _log_fmt = f"COMMIT TIME: {datetime.now()}:\n"
            self.log(_log_fmt, None)

    def rollback(self):
        do_log = self.get_transaction_status()
        super(LoggingConnection, self).rollback()
        if do_log:
            _log_fmt = f"ROLLBACK TIME: {datetime.now()};"
            self.log(_log_fmt, None)
