from contextlib import contextmanager
import telebot, psycopg2, schedule, datetime, uuid
from datetime import datetime, timedelta
from threading import Thread
import threading
from config import *

bot = telebot.TeleBot(BOT_TOKEN)

@contextmanager
def get_connect():
    connect = psycopg2.connect(
        dbname=DB_NANE,
        user=DB_USERNAME,
        password=DB_PASSWORD,
    )
    try:
        yield connect
    finally:
        connect.close()

with get_connect() as connect:
    with connect.cursor() as c:
        c.execute("select version();")
        info_db = c.fetchone()
        print(f"{datetime.now()} | [INFO] | Бот подключен к базе: {info_db[0]}")

def check_telegram_id(connect, telegram_id):
    with connect.cursor() as c:
        c.execute("select * from telegram_users where telegram_id=%s;", (telegram_id,))
        return c.fetchone()

def add_new_telegram_user(connect, telegram_id, user_first_name, user_last_name, user_name):
    error_uuid = uuid.uuid1()
    with connect.cursor() as c:
        c.execute("INSERT INTO telegram_users (telegram_id, first_name, last_name, username) VALUES(%s, %s, %s, %s) RETURNING id;",(telegram_id, user_first_name, user_last_name, user_name))
        connect.commit()
        new_user_id = c.fetchone()
        if not new_user_id[0]:
            print(f"{datetime.now()} | [INFO] | {user_first_name} {user_last_name} id:{telegram_id} - [ERROR {error_uuid}] Не удалось добавить пользователя, что-то пошло не по плану")
        else:
            print(f"{datetime.now()} | [INFO] | {user_first_name} {user_last_name} id:{telegram_id} - [INSERT] Пользователь успешно зарегистрировался в системе, добавлена запись в telegram_users под id:{new_user_id[0]}")
            true = f"Поздравляю вы зарегистрировались, Ваш персанльный id: {new_user_id[0]}\n"
            false = f"К сожалению возникла ошибка!\nПросьба связаться с @DeLipFin и передать\n{error_uuid}"
            message =  f"Уважаемый(ая), {user_first_name}!\n{true if new_user_id[0] else false}"
            return message

def check_status_telegram_user(connect, tu_id):
    with connect.cursor() as c:
        c.execute("select * from telegram_users where id=%s;", (tu_id,))
        user = c.fetchone()
        message = "Подписка неактивна, уведомления не приходят!"
        if user[5]:
            text = ['[Праздники]','[Дни рождения]','[Напоминалка]','Уведомления включены','Уведомления выключены']
            holiday = f"🔕 {text[0]} {text[4]}" if not user[6] else f"🔔 {text[0]} {text[3]}"
            c.execute("select * from check_list_birthdays where tu_id=%s;", (tu_id,))
            birthday = c.fetchone()            
            birthday = f"🔕 {text[1]} {text[4]}" if not user[7] else f"🔔 {text[1]} {text[3]}" if birthday else f"❗️ {text[1]} Добавьте кого-нибудь /add_users"
            c.execute("select * from check_list_notifications where tu_id=%s;", (tu_id,))
            notification = c.fetchone()
            notification = f"🔕 {text[2]} {text[4]}" if not user[8] else f"🔔 {text[2]} {text[3]}" if notification else f"❗️ {text[2]} Добавьте что-нибудь /add_notifications"
            message = holiday + '\n' + birthday + '\n' + notification
        return message

@bot.message_handler(commands=['start'])
def start_message(message):
    telegram_id = message.from_user.id
    user_first_name = message.from_user.first_name
    user_last_name = message.from_user.last_name
    user_name = message.from_user.username
    with get_connect() as conn:
        user = check_telegram_id(conn, telegram_id)
        if not user:
            new_user = add_new_telegram_user(conn, telegram_id, user_first_name, user_last_name, user_name)
            bot.send_message(message.from_user.id, f"{new_user}")
        else:
            check_status = check_status_telegram_user(conn, user[0])
            bot.send_message(message.from_user.id, f"Давно не виделись, {user[2]}!\nВаш персональный id: {user[0]}\n{check_status}")
        

# @bot.message_handler(func=lambda _: True)
# def message_handler(message):
#     print(message) 

# def main():
#     # schedule.every().day.at('00:35').do(holidays)
#     # schedule.every().day.at('00:40').do(holidays)
#     # schedule.every(10).seconds.do(holidays)
#     while True:
#         schedule.run_pending()

if __name__ == '__main__':
    # main()
    # th1 = threading.Thread(target=main, daemon=True)
    # th1.start()
    # th2 = threading.Thread(target=birthday_add, daemon=True)
    # th2.start()
    bot.polling(none_stop=True)