from urllib.parse import urlparse


def get_env_vars(container, db_name=None):
    connection_string = urlparse(container.get_connection_url())
    postfix = f"_{db_name}" if db_name else ""

    return {
        "PGM_PREFIX": "TESTCASE",
        f"TESTCASE_PORT{postfix}": str(connection_string.port),
        f"TESTCASE_DB{postfix}": connection_string.path[1:],
        f"TESTCASE_USER{postfix}": connection_string.username,
        f"TESTCASE_HOST{postfix}": connection_string.hostname,
        f"TESTCASE_PASSWORD{postfix}": connection_string.password,
        f"TESTCASE_SCHEME{postfix}": connection_string.scheme,
    }
