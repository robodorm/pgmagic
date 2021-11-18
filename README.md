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
      # Prefix is important, because ALL env vars with that prefix will be
      # loaded into the configuration
      PGM_PREFIX: PG
      
      # Define the database with the name "default". Name used in the
      # configuration to access the database.
      PG_PASSWORD: db_one
      PG_USER: db_one
      PG_DB: db_one
      PG_HOST: db_one

      # Definition of a second database with name "TWO". Name could be any.
      # All missed parameters will be set to defaults*
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

*defaults:
```
"PASSWORD": "postgres",
"USER": "postgres",
"DB": "postgres",
"HOST": "postgres",
"PORT": 5432
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
