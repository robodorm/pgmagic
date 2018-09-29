# pgmagic

Postgres connector for sqlalchemy

# Features
  - Multiple databases
  - Loading configuration from environment

### Installation

```sh
$ pip install -e git+https://github.com/ecohq/pgmagic.git#egg=pgmagic --upgrade
```

### Example usage

docker-compose.yml:

```
version: '2'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      PG_PASSWORD_ONE: db_one
      PG_USER_ONE: db_one
      PG_DB_ONE: db_one
      PG_HOST_ONE: db_one

      PG_PASSWORD_TWO: db_two
      PG_USER_TWO: db_two
      PG_DB_TWO: db_two
      PG_HOST_TWO: db_two
    links:
      - db_one
      - db_two
    restart: always

  db_one:
    image: postgres:latest
    environment:
      POSTGRES_PASSWORD: db_one
      POSTGRES_USER: db_one
      POSTGRES_DB: db_one

  db_two:
    image: postgres:latest
    environment:
      POSTGRES_PASSWORD: db_two
      POSTGRES_USER: db_two
      POSTGRES_DB: db_two
```

app.py:

```
from pgmagic import get_base, session

# default model location: db_one
class DataModelOne(get_base("one")):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)

# copy record from db_one to db_two
with session("two") as s:
        # by default DataModelOne located in the db_one
        s.add(DataModelOne.query.filter(DataModelOne.id = 1).first())
```
