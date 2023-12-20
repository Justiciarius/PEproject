import asyncio
import logging

import aiogram
import psycopg2
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from get_news_functions import send_latest_news_periodically

logging.basicConfig(level=logging.INFO)
bot = Bot(token="6587120664:AAF5R3IV4Sw4mDEQNdjFvjoKNszB0aIf964")
dp = Dispatcher()

# Dictionary for saving chosen categories by user
user_categories = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # новости отправляются в чат с ботом
    await message.answer("Привет! Я бот-парсер новостей.")

@dp.message(Command("info"))
async def cmd_info(message: types.Message):
    await message.answer("Я отправляю новости))")


@dp.message(Command("news_by_key"))
async def cmd_news_by_key(message: types.Message):
    await message.answer(
        "Отлично! Начни сообщение как \"Ключ:\" и напиши ключ, по которому хочешь найти последние новости.")


@dp.message(lambda message: message.text.lower().startswith('ключ:'))
async def process_keywords(message: types.Message):
    # Извлекаем ключевые слова из текста сообщения
    global conn, cursor
    key_words = message.text.lower().split('ключ: ')[1:]
    await message.answer(f"Принял ключ: {key_words[0]}.")
    await message.answer(f"Ищу новости...")
    try:
        conn = psycopg2.connect(host='localhost', port=5432, database='news', user='postgres', password='superuser')
        cursor = conn.cursor()

        query = "SELECT title, pubDate, category,content, link FROM news_articles WHERE keywords @> %s"

        cursor.execute(query, ([key_words[0]],))
        news_by_key = cursor.fetchall()

        if (news_by_key):
            for curr_news in news_by_key:
                if curr_news:
                    news_message = f"{curr_news[0]}"
                    news_message += f"\n\n{curr_news[3]}"
                    news_message += f"\n\nСсылка на статью: {curr_news[4]}"

                    await bot.send_message(message.chat.id, news_message)
        else:
            await bot.send_message(message.chat.id,
                                   "К сожалению, новости по ключу не найдены.")

    except psycopg2.Error as e:
        # Обработка ошибок подключения
        print(f"Ошибка при подключении к базе данных: {e}")
        return None
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()




@dp.callback_query(lambda c: c.data.startswith('my_categories_add'))
async def my_categories_add(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    buttons = [
        [
            types.InlineKeyboardButton(text="Политика", callback_data="category_Политика"),
            types.InlineKeyboardButton(text="Спорт", callback_data="category_Спорт"),
        ],
        [
            types.InlineKeyboardButton(text="Развлечения", callback_data="category_Развлечения"),
            types.InlineKeyboardButton(text="Топ", callback_data="category_Топ"),
        ],
        [
            types.InlineKeyboardButton(text="Здоровье", callback_data="category_Здоровье"),
            types.InlineKeyboardButton(text="Технологии", callback_data="category_Технологии"),
        ],
        [
            types.InlineKeyboardButton(text="Еда", callback_data="category_Еда"),
            types.InlineKeyboardButton(text="Наука", callback_data="category_Наука"),
        ],
    ]

    builder = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await bot.send_message(
        chat_id,
        "Выберите категории. При выборе категории, на которую вы уже подписаны, произойдёт отписка.",
        reply_markup=builder
    )


@dp.message(Command("my_categories"))
async def my_categories(message: types.Message):
    id = message.chat.id
    buttons = [
        [
            types.InlineKeyboardButton(text="Выбрать категории", callback_data="my_categories_add")
        ],
        [
            types.InlineKeyboardButton(text="Мои категории", callback_data="my_categories_set")
        ]
    ]
    builder = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        "Что вы хотите сделать?",
        reply_markup=builder
    )

@dp.callback_query(lambda c: c.data.startswith('my_categories_set'))
async def my_categories_set(callback_query: types.CallbackQuery):

    id = callback_query.message.chat.id
    await bot.send_message(id, f"Ваши категории: {', '.join(user_categories[id])}")
    # Выкидывает ошибку если пусто в категориях :((((

@dp.callback_query(lambda c: c.data.startswith('category_'))
async def categories_buttons(callback_query: types.CallbackQuery):
    category_text = callback_query.data.split('_')[1]  # Извлекаем текст категории
    id = callback_query.message.chat.id
    if id not in user_categories:
        user_categories[id] = set()
    if category_text in user_categories[id]:
        user_categories[id].remove(category_text)
        await bot.send_message(id, f"Вы отписались от категории: {category_text}")
    else:
        user_categories[id].add(category_text)
        await bot.send_message(id, f"Вы подписались на категорию: {category_text}")

@dp.message(Command("start_send_news"))
async def start_send_news(message: types.Message):
    if(message.chat.id not in user_categories):
        user_categories[message.chat.id] = {}
    global send_news_enabled
    send_news_enabled = True


    await message.answer("Настройка завершена! Я буду присылать новости раз в час. Если вы не выбрали категории, то я буду присылать все новости, которые смог найти для вас!")

    # Планирование отправки новостей
    loop.create_task(send_latest_news_periodically(bot, user_categories[message.chat.id], message.chat.id, send_news_enabled))

@dp.message(Command("stop_send_news"))
async def stop_send_news(message: types.Message):
    # Прекращаем отправку новостей
    send_news_enabled = False
    await message.answer("Останавливаю рассылку. Возвращайтесь к нам после настройки!")

@dp.message()
async def handle_random_text(message: types.Message):
    await message.answer("К сожалению, я вас не понимаю. Прочитайте информацию о работе бота по команде /info")

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()

