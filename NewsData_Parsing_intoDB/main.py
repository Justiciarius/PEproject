import configparser
import time

import psycopg2
import requests

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

        if keywords:
            keywords = [key.lower() for key in keywords]

        # Добавляем запись в бд
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
            print("News added.")


if __name__ == '__main__':
        api_url = "https://newsdata.io/api/1/news?apikey=pub_35073ff8abdeb696be3aabe97c0e79a89e69c&timeframe=15m&timezone=Europe/Moscow"

        params = {
            'language': 'ru'
        }
        while(True):
            try:
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
                    insert_article_toBD(article_id,title,link,keywords,creator,description,content,country,category,language,pubDate)

                    time.sleep(900)
            except Exception as e:
                print(f"Exception catched: {e}")
                time.sleep(60)





