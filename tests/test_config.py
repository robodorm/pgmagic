import os
import unittest
from unittest import mock

from pgmagic.cfloader import pg_cfg, Postgres


class TestConfigSingleton(unittest.TestCase):

    def test_config_exists_single(self):
        config_a = Postgres()
        config_b = Postgres()

        self.assertIsNotNone(config_a)
        self.assertIsNotNone(config_b)
        self.assertEqual(config_a, config_b)

    def test_load_default_config(self):
        default_config = pg_cfg("default")
        self.assertEqual("postgresql://postgres:postgres@postgres:5432/postgres", default_config)

    def test_load_custom_prefix(self):
        env_vars = {
            "PGM_PREFIX": "OLOLO",
            "OLOLO_PORT": "12300",
        }

        with mock.patch.dict(os.environ, env_vars):
            custom_config = pg_cfg(database="default")

        self.assertEqual("postgresql://postgres:postgres@postgres:12300/postgres", custom_config)

    @mock.patch.dict(os.environ, {
        "PG_PASSWORD": "password",
        "PG_USER": "user",
        "PG_DB": "database",
        "PG_HOST": "hostname",
        "PG_PORT": "123",
    })
    def test_load_custom_config_one_db(self):
        from pgmagic.cfloader import pg_cfg

        self.assertTrue("PG_PASSWORD" in os.environ.keys())
        self.assertEqual("password", os.getenv("PG_PASSWORD"))

        default_config = pg_cfg("default")
        self.assertIsNotNone(default_config)
        self.assertEqual("postgresql://user:password@hostname:123/database", default_config)

    @mock.patch.dict(os.environ, {
        "PG_PASSWORD": "password",
        "PG_USER": "user",
        "PG_DB": "database",
        "PG_HOST": "hostname",
        "PG_PORT": "123",
        "PG_PASSWORD_READONLY": "password_ro",
        "PG_USER_READONLY": "user_ro",
        "PG_DB_READONLY": "database_ro",
        "PG_HOST_READONLY": "hostname_ro",
        "PG_PORT_READONLY": "12300",
    })
    def test_load_custom_config_multiple(self):
        from pgmagic.cfloader import pg_cfg

        default_database = pg_cfg("default")
        readonly_database = pg_cfg("READONLY")

        self.assertEqual("postgresql://user:password@hostname:123/database", default_database)
        self.assertEqual("postgresql://user_ro:password_ro@hostname_ro:12300/database_ro", readonly_database)


if __name__ == '__main__':
    unittest.main()
