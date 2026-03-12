import psycopg
import os
from app.core.config import config
# from core.logger_setup import logger

# logger("db connection")

connection_string = config.DATABASE_URL

# Connect with neon DB
try:
    with psycopg.connect(connection_string) as conn:
        # logger.info('Connection established with postgresql')
        print('Connection established with postgresql')

        with conn.cursor() as curr:
            curr.execute('CREATE TABLE IF NOT EXISTS test_table(id serial PRIMARY KEY, data varchar (255));')
            curr.execute('INSERT INTO test_table (data) VALUES (%s)', ("test_data",))
            curr.execute("SELECT * FROM test_table;")

            records = curr.fetchall()
            for row in records:
                print(row)

except Exception as error:
    print(f"Error connecting to the database {error}")
