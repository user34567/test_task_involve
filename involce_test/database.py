import psycopg2
from const import DBNAME
from datetime import datetime


def write(amount, currency, description, conn):
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    query = "INSERT INTO orders( amount, currency, date, description) VALUES (" + str(amount) + "," + str(currency)
    query = query + ", TIMESTAMP '" + date + "','" + description + "')"
    conn.cursor().execute(query)


def get_conn():
    return psycopg2.connect(database=DBNAME)


# def commit(conn):
#     conn.commit()
#
#
# def rollback(conn):
#     conn.rollback()




