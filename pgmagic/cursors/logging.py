import psycopg2.extensions


class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, query, vars=None):
        try:
            return super(LoggingCursor, self).execute(query, vars)
        finally:
            query_str = self.query.decode() \
                if isinstance(self.query, bytes) \
                else self.query
            self.connection.log(f"{query_str}", self)
