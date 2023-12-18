import configparser
import psycopg2
import requests

db_params = {
    'host': 'localhost',
    'port': '5432',
    'database': 'news',
    'user': 'postgres',
    'password': 'superuser',
}

global global_config
global_config = None

def read_config():
    # Заменить путь до конфига и параметры в нем!!
    config = configparser.ConfigParser()
    config.read('C:/Users/sasharykova/Desktop/News_bot/config.ini')
    return config

def insert_article_toBD(article_id, title,link,keywords,creator,description,content,country,category,language,pubDate):
    global connection, cursor, global_config
    try:

        if global_config is None:
            global_config = read_config()

        db_host = global_config.get('Database', 'host')
        db_port = global_config.get('Database', 'port')
        db_name = global_config.get('Database', 'database')
        db_user = global_config.get('Database', 'user')
        db_password = global_config.get('Database', 'password')


        conn = psycopg2.connect(
                            host= db_host,
                            port= db_port,
                            database= db_name,
                            user= db_user,
                            password= db_password)
        cursor = conn.cursor()

        # Добавляем запись в бд
        # Запрс такой: Добавляем в запись, если конфликт по id, тогда ничего не делаем. Тогда добавляются уникальные статьи только
        insert_query = """INSERT INTO news_articles(article_id,title, link, keywords, creator, description, content, country, category, language,pubDate) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s,%s) ON conflict(article_id) do nothing;"""

        # Выполнение запроса с данными новой записи
        cursor.execute(insert_query,
                       (article_id,title, link, keywords, creator, description, content, country, category, language,pubDate))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")

    finally:
        # Закрытие соединения (важно для освобождения ресурсов)
        if conn:
            cursor.close()
            conn.close()
            print("Соединение с базой данных закрыто.")


if __name__ == '__main__':
    api_url = "https://newsdata.io/api/1/news?apikey=pub_309362a0eee274b94757fdb8cdf4e887046a4"

    # Запрос с параметрами - нам нужны только новости на русском
    params = {
        'language': 'ru'
    }
    while(True):
        # Отправялем запросы на сервер раз час???7
        # time.sleep(3600)??????
        response = requests.get(url=api_url, params=params)
        news_data = response.json()

        # Перебираем полученный json-файл
        for news_item in news_data['results']:
            article_id = news_item.get('article_id')
            title = news_item.get('title')
            link = news_item.get('link')
            keywords = news_item.get('keywords')
            creator = news_item.get('creator')
            description = news_item.get('description')
            content = news_item.get('content')
            country = news_item.get('country')
            category = news_item.get('category')
            language = news_item.get('language')
            pubDate = news_item.get('pubDate')

            # Добавляем статьи в БД
            # P.S. Наверное, не очень хорошо, что каждую итерацию подключение открывается и закрывается
            insert_article_toBD(article_id,title,link,keywords,creator,description,content,country,category,language,pubDate)





