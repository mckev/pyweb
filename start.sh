#!/bin/sh
# Note:
#    - Only 1 process is supported by psycopg2.pool (http://initd.org/psycopg/docs/faq.html#problems-with-transactions-handling: "Psycopg's connections can't be shared across processes (but are thread safe).")
#    - When changing the number of uwsgi threads, please also modify maxconn of psycopg2.pool in start.py.
# /opt/python3.4/bin/uwsgi --master --uwsgi-socket localhost:9000 --stats :9191 --processes 1 --threads 20 --need-app --wsgi-file start.py
/opt/python3.4/bin/uwsgi --master --uwsgi-socket /tmp/uwsgi.sock --chmod-socket=777 --http :9090 --stats :9191 --processes 1 --threads 20 --need-app --wsgi-file start.py
