import os.path
import sqlite3
from sqlite3 import Error
from options import BASE_DB_PATH


def create_connection():
    connection = None
    try:
        connection = sqlite3.connect(BASE_DB_PATH)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        return connection


def set_up_db():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''
CREATE TABLE IF NOT EXISTS ProxyUsers (
id INTEGER PRIMARY KEY,
login TEXT NOT NULL,
password TEXT NOT NULL)
''')

    connection.commit()
    connection.close()


class ProxyDataBase:
    def __init__(self):
        set_up_db()
        self.__connection = create_connection()
        self.__cursor = self.__connection.cursor()

    def add_user(self, login: str, password: str):
        self.__cursor.execute('INSERT INTO ProxyUsers (login, password) VALUES (?, ?)', (login, password))
        self.__connection.commit()

    def is_user_registered(self, login: str, password: str) -> bool:
        self.__cursor = self.__connection.cursor()
        self.__cursor.execute('''
                SELECT login, password
                FROM ProxyUsers
                WHERE login = ?''', (login,))
        self.__results = self.__cursor.fetchall()
        if len(self.__results) == 1 and self.__results[0][1] == password:
            return True
        return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__connection.close()




