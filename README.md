# pgmagic

Postgres connector for sqlalchemy

# Features
  - Multiple databases
  - Loading configuration from environment

### Installation

```sh
$ pip install -e git+https://github.com/robodorm/pgmagic.git#egg=pgmagic --upgrade
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
      # optional, "PG" - already set as a default prefix
      PGM_PREFIX: PG

      PG_PASSWORD: db_one
      PG_USER: db_one
      PG_DB: db_one
      PG_HOST: db_one

      # all missed parameters
      # will be set to defaults
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

# default model DB is "default"
class DataModelOne(get_base()):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)

# copy record from "default" to "db_two"
with session("TWO") as s:
        s.add(DataModelOne.query.filter(DataModelOne.id = 1).first())
```

### (!) Project is not well tested yet (!!!)
