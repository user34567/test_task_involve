import psycopg2
from datetime import datetime


class Database:
    def __init__(self):
        self.__conn = psycopg2.connect(database="involve_test_db")
        self.__cursor = self.__conn.cursor()

    def commit(self):
        self.__conn.commit()

    def execute(self, query):
        self.__cursor.execute(query)
        if query[0] == "I":
            self.__conn.commit()
        if query[0] == "S":
            return self.__cursor.fetchall()

    def get_last_id(self):
        self.__cursor.execute("SELECT MAX(id) FROM orders")
        return self.__cursor.fetchall()[0][0]

    def write(self, amount, currency, description):
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        query = "INSERT INTO orders( amount, currency, date, description) VALUES (" + str(amount) + "," + str(currency)
        query = query + ", TIMESTAMP '" + date + "','" + description + "')"
        self.__cursor.execute(query)
        self.__conn.commit()
