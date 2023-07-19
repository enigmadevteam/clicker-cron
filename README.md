# Clicker-Cron

## Build & Run
1. `docker build -t clicker-cron-app .`
2. `docker run -p 8000:8000  clicker-cron-app`

## Configure
These parameters are located and available for customization in the `const.py` file:

- `POSTGRES_URL` - URL for PostgreSQL (format: `postgresql://<user>:<password>@<host>:<port>/<database>`)
- `ASYNC_POSTGRES_URL` - URL for async PostgreSQL (format: `postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>`)
- `WAIT_TIME` - time between addition actions, in seconds
- `INDEX_COLUMN` - index of the column for which the summation action will be performed 