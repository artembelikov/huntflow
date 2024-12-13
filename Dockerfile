FROM postgres:15

# Устанавливаем переменные окружения для PostgreSQL
ENV POSTGRES_USER=test_user
ENV POSTGRES_PASSWORD=test_password
ENV POSTGRES_DB=test_db

# Копируем дамп в контейнер
COPY test/data/dump_test_db.sql /tmp/dump_test_db.sql

# Копируем файлы конфигурации
COPY test/data/postgresql.conf /etc/postgresql/postgresql.conf

WORKDIR /tmp

# Переключаемся на пользователя postgres
USER postgres

# Выполняем команды для создания расширения и привилегий
RUN /usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/data && \
    /usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/data -l /tmp/logfile start && \
    psql -c "CREATE ROLE test_user WITH LOGIN PASSWORD 'test_password';" && \
    psql -c "CREATE DATABASE test_db OWNER test_user;" && \
    psql -d test_db -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;" && \
    psql -d test_db -c "GRANT pg_read_all_settings TO test_user;" && \
    pg_restore -U test_user -d test_db /tmp/dump_test_db.sql && \
    /usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/data stop

# Копируем файл pg_hba.conf
COPY test/data/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf

# Возвращаем пользователя root для возможных других настроек
USER root

# Настройка конфигурации при запуске
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]