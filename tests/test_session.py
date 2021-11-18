import os
import tracemalloc
import unittest
from unittest import mock

from testcontainers.postgres import PostgresContainer

import pgmagic
from tests.helper import get_env_vars


class TestSession(unittest.TestCase):

    def test_create_session(self):
        with PostgresContainer("postgres:14.1") as c:
            env_vars = get_env_vars(c)

            with mock.patch.dict(os.environ, env_vars):
                custom = pgmagic.pg_cfg(database="default")
                self.assertEqual(custom, c.get_connection_url())

    def test_nested_sql_query(self):
        # launching first container
        with PostgresContainer("postgres:14.1") as database_first:
            env_vars = get_env_vars(database_first, "first")

            # launching second container
            with PostgresContainer("postgres:14.1") as database_second:
                env_vars = {**get_env_vars(database_second, "second"), **env_vars}

                # patching ENV vars with connection to both containers
                with mock.patch.dict(os.environ, env_vars):
                    pgmagic.Postgres().load_params()

                    # starting parent session
                    with pgmagic.session("first") as s:
                        ret_first = s.execute("SELECT 1").fetchone()

                        # starting nested session
                        with pgmagic.session("second") as s:
                            ret_second = s.execute("SELECT 1").fetchone()

        self.assertEqual(ret_first[0], ret_second[0])


if __name__ == '__main__':
    unittest.main()
