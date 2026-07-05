#!/usr/bin/env sh
set -eu

python <<'PY'
import os
import sys
import time

import psycopg

host = os.environ.get("POSTGRES_HOST", "postgres")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
dbname = os.environ.get("POSTGRES_DB", "konglomerat")
user = os.environ.get("POSTGRES_USER", "postgres")
password = os.environ.get("POSTGRES_PASSWORD", "")
deadline = time.time() + int(os.environ.get("POSTGRES_WAIT_TIMEOUT", "60"))

while True:
    try:
        with psycopg.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            connect_timeout=3,
        ):
            break
    except psycopg.OperationalError as exc:
        if time.time() >= deadline:
            print(f"Postgres is unavailable after waiting: {exc}", file=sys.stderr)
            raise
        print("Waiting for Postgres...", flush=True)
        time.sleep(2)
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
