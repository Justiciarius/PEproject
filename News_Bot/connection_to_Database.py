import configparser
import psycopg2

def connectdb():
    try:
        # Чтение конфигурации из файла
        config = configparser.ConfigParser()
        config.read('C:/Users/sasharykova/Desktop/News_bot/config.ini')
        # Параметры подключения к базе данных из конфига
        db_params = {
            'host': config['Database']['host'],
            'port': config['Database']['port'],
            'user': config['Database']['user'],
            'password': config['Database']['password'],
            'database': config['Database']['database'],
        }

        conn = psycopg2.connect(**db_params)

        return conn
    except psycopg2.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
