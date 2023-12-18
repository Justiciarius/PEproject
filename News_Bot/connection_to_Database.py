import configparser
import psycopg2

# Чтение конфигурации из файла
config = configparser.ConfigParser()
config.read('config.ini')

def connectdb():
    # Параметры подключения к базе данных из конфига
    db_params = {
        'host': config['database']['host'],
        'port': config['database']['port'],
        'user': config['database']['user'],
        'password': config['database']['password'],
        'database': config['database']['database'],
    }

    conn = psycopg2.connect(**db_params)

    return conn
