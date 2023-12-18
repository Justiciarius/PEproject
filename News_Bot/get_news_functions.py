import asyncio
import psycopg2
from connection_to_Database import connectdb
from datetime import datetime, timedelta

# Получаем последние новости из БД
async def get_latest_news(categories):
    try:
        #conn = connectdb()
        conn = psycopg2.connect(host='localhost', port=5432, database='news', user='postgres', password='superuser')
        cursor = conn.cursor()

        query = "SELECT title, pubDate, category,content, link FROM news_articles"
        conditions = []

        for cat in categories:
            if cat == 'Политика':
                conditions.append("category='{politics}'")
            elif cat == 'Спорт':
                conditions.append("category='{sports}'")
            elif cat == 'Развлечения':
                conditions.append("category='{entertainment}'")
            elif cat == 'Здоровье':
                conditions.append("category='{health}'")
            elif cat == 'Топ':
                conditions.append("category='{top}'")
            elif cat == 'Технологии':
                conditions.append("category='{technology}'")
            elif cat == 'Наука':
                conditions.append("category = '{science}'")

        current_datetime = datetime.now()

        # Текущее время минус 1 час (почему не использую читай .txt)
        past_datetime = current_datetime - timedelta(hours=1)

        if conditions:
            query = f"{query} WHERE {' OR '.join(conditions)} AND pubDate > '2023-12-18 10:00:00';"

        cursor.execute(query)
        latest_news = cursor.fetchall()

        return latest_news
    except psycopg2.Error as e:
        # Обработка ошибок подключения
        print(f"Ошибка при подключении к базе данных: {e}")
        return None
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()

# Отправка последних новостей
async def send_latest_news(bot,user_categories,chat_id):

    latest_news = await get_latest_news(user_categories)
    if(latest_news):
        for curr_news in latest_news:
            if curr_news:
                news_message = f"Заголовок: {curr_news[0]}"
                news_message += f"\nДата публикации: {curr_news[1]}"
                news_message += f"\nКатегория: {curr_news[2]}"
                news_message += f"\n\nСодержание: {curr_news[3]}"
                news_message += f"\nСсылка на статью: {curr_news[4]}"

                await bot.send_message(chat_id, news_message)
    else:
        await bot.send_message(chat_id, "За последний час ничего не случилось. Но надеюсь, что ваш день проходит хорошо!")

# Повторяем отправку каждый час
async def send_latest_news_periodically(bot, user_categories, chat_id, send_news_enabled):
    if(send_news_enabled):
        while True:
            await send_latest_news(bot, user_categories, chat_id)
            await asyncio.sleep(3600)
