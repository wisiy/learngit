import os
import mysql.connector

SECRET_KEY = os.urandom(24)
# 建立数据库连接
HOST = "127.0.0.1"
PORT = "3306"
DATABASE = "thesis"
USER = "root"
PASSWORD = "admin1234"
CHARSET = "utf8"
DB_URI = "mysql+mysqlconnector://{}:{}@{}:{}/{}?charset={}".format(USER, PASSWORD, HOST, PORT, DATABASE, CHARSET)
SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False
