#!/usr/bin/env bash

docker exec -t postgres-test pg_dump -U test_user -d test_db -F c -b -v -f /tmp/dump_test_db.sql
docker cp postgres-test:/tmp/dump_test_db.sql ./dump_test_db.sql