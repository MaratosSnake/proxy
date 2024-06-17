import sqlite3
from sqlite3 import Error
from options import BASE_DB_PATH
from proxy_logger import logger


def create_connection():
    connection = None
    try:
        connection = sqlite3.connect(BASE_DB_PATH)
        logger.info("Connection to SQLite DB successful")
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
    return connection


class ProxyDataBase:
    def __init__(self):
        # create connection to database
        self.__connection = set_up_db()
        self.__cursor = self.__connection.cursor()

    def add_user(self, login: str, password: str):
        """
        Adding user to db after registration
        :param login: user login
        :param password: user password
        :return:
        """
        self.__cursor.execute('INSERT INTO ProxyUsers (login, password) VALUES (?, ?)', (login, password))
        self.__connection.commit()

    def is_user_registered(self, login: str, password: str) -> bool:
        """
        Checks user registration in proxy db
        :param login: user login
        :param password: user password
        :return: true if user has already registered else false
        """
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

    def get_client_data(self):
        while True:
            is_reg = input('Have you already registered? [y/n] >> ').lower()
            if is_reg == 'y':
                login = input('Enter your login >> ')
                password = input('Enter your password >> ')
                break
            elif is_reg == 'n':
                login = input('Enter your login >> ')
                while True:
                    password = input('Enter your password >> ')
                    conf_password = input('Confirm your password >> ')
                    if password == conf_password:
                        self.add_user(login, password)
                        break
                    else:
                        print('Passwords are different')
                break
            else:
                print('Please answer correctly')
        return login, password






