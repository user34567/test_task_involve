import psycopg2
from const import DBNAME, DATABASE_URL
import os


print(DATABASE_URL == os.environ.get('DATABASE_URL'))


def write(amount, currency, description, conn):

    query = "INSERT INTO orders( amount, currency, description) VALUES (" + str(amount) + "," + str(currency)
    query = query + ",'" + description + "')"
    conn.cursor().execute(query)


def get_conn():
    #return psycopg2.connect(database=DBNAME)
    return psycopg2.connect(DATABASE_URL)


# def commit(conn):
#     conn.commit()
#
#
# def rollback(conn):
#     conn.rollback()




