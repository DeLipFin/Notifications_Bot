from contextlib import contextmanager
import telebot, psycopg2, schedule, datetime, uuid
from datetime import datetime, timedelta
from threading import Thread
import threading
from Config import *

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

# Проверка подключения к БД
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
        c.commit()
        new_user_id = c.fetchone()
        if not new_user_id[0]:
            print(f"{datetime.now()} | [INFO] | {user_first_name} {user_last_name} id:{user_id} - [ERROR {error_uuid}] Не удалось добавить пользователя, что-то пошло не по плану")          
        else:  
            print(f"{datetime.now()} | [INFO] | {user_first_name} {user_last_name} id:{user_id} - [INSERT] Пользователь успешно зарегистрировался в системе, запись в telegram_users под id:{new_user_id[0]} добавлена")

def check_status_telegram_user(connect, telegram_id):
    with connect.cursor() as c:
        c.execute("select * from telegram_users where telegram_id=%s;", (telegram_id,))
        user = c.fetchone()
        message = "Подписка неактивна, уведомления не приходят!"
        if user[6]:
            message = (
                f"{'🔔' if user[7] else '🔕'} Уведомления о днях рождения\n"
                f"{'🔔' if user[8] else '🔕'} Уведомления о праздников\n"
                f"{'🔔' if user[9] else '🔕'} Уведомления о Ваших напоминаний\n"
            )
        reply = message
        return reply

@bot.message_handler(commands=['start'])
def start_message(message):
    telegram_id = message.from_user.id
    user_first_name = message.from_user.first_name
    user_last_name = message.from_user.last_name
    user_name = message.from_user.username
    with get_connect() as conn:
        user = check_telegram_id(conn, telegram_id)
        check_status = check_status_telegram_user(conn, telegram_id)
        if not user:  # Пользователь не зарегестрирован в бд
            add_new_telegram_user(telegram_id, user_first_name, user_last_name, user_name)  # Добавляем пользователя в бд
        else:  # Пользователь есть в бд
            bot.send_message(message.from_user.id, f"Давно не виделись, {user[2]}!\nВаш персональный id: {user[0]}\n{check_status}")
        

if __name__ == '__main__':
    bot.polling(none_stop=True)

# @bot.message_handler(commands=['start'])
# def start_message(message):
#     user_id = message.from_user.id
#     user_first_name = message.from_user.first_name
#     user_last_name = message.from_user.last_name
#     user_name = message.from_user.username
#     error_uuid = uuid.uuid1()
#     cursor.execute(f"select * from telegram_users where telegram_id={user_id};")
#     telegram_user = cursor.fetchone()
#     print(f"{datetime.now()} | [INFO] | {user_first_name} {user_last_name} id:{user_id} - Воспользовался командой /start")
#     if  not telegram_user:
#         bot.send_message(message.from_user.id, f"Добро пожаловать, {user_first_name}!\nВы тут первый раз!?\nДавайте занесу Вас в систему, нужно написать? (Да/Нет)")
#         @bot.message_handler(content_types=['text'])
#         def start(message): 
#             if  message.text.lower() == 'да':
#                 cursor.execute(f"INSERT INTO telegram_users (telegram_id, first_name, last_name, username) VALUES({user_id}, '{user_first_name}', '{user_last_name}', '{user_name}') RETURNING id;")
#                 conn.commit()
#                 telegram_user_id = cursor.fetchone()
#                 cursor.execute(f"select * from telegram_users where telegram_id={user_id};")
#                 check_telegram_user_id = cursor.fetchone()
#                 if not check_telegram_user_id:
#                     bot.send_message(message.from_user.id, f"Уважаемый(ая), {user_first_name}!\nК сожалению возникла ошибка!\n"
#                                                             f"Просьба связаться с @DeLipFin и передать\n{error_uuid}")
#                     print(f"{datetime.now()} | [INFO] | {user_first_name} {user_last_name} id:{user_id} - [ERROR {error_uuid}] Не удалось добавить пользователя, что-то пошло не по плану")          
#                 else:  
#                     bot.send_message(message.from_user.id, f"Добавил Вас в систему {user_first_name}!\nВаш персональный id: {telegram_user_id[0]}\nВсе уведомления включены по умолчанию!\nЕсли хотите исправить, используйте /notification")
#                     print(f"{datetime.now()} | [INFO] | {user_first_name} {user_last_name} id:{user_id} - [INSERT] Пользователь успешно зарегистрировался в системе, запись в telegram_users под id:{telegram_user_id[0]} добавлена")
#                     bot.send_message(message.from_user.id, f"Сейчас Вы можете добавлять в список своих ")
#             elif message.text.lower() == 'нет':
#                 bot.send_message(message.from_user.id, f"Больше не буду Вас беспокоить, {user_first_name}!\nНо Вы всегда можете написать \"да\" для завершении регистрации!")
#                 print(f"{datetime.now()} | [INFO] | {user_first_name} {user_last_name} id:{user_id} - Пользователь отказался от регистрации")
#             else:
#                 bot.send_message(message.from_user.id, f"Напишите пожалуйста Да/Нет для завершении регистрации!\nЛибо воспользуйтесь командой /help")
#                 print(f"{datetime.now()} | [INFO] | {user_first_name} {user_last_name} id:{user_id} - Пользователь написал \"{message.text}\"")
#     else:
#         if  telegram_user[4] == True:
#             bot.send_message(message.from_user.id, f"Давно не виделись, {telegram_user[2]}!\nВаш персональный id: {telegram_user[0]}\n"
#                                                     f"Подписка включена!\nЕсли хотите выключить, используйте команду /notification")
#         else:
#             bot.send_message(message.from_user.id, f"Давно не виделись, {telegram_user[2]}!\nВаш персональный id: {telegram_user[0]}\n"
#                                                     f"Подписка отключена у Вас!\nЕсли хотите включить, используйте команду /notification")


# # @bot.message_handler(func=lambda _: True)
# # def message_handler(message):
# #     print(message) 

# def main():
#     # schedule.every().day.at('00:35').do(holidays)
#     # schedule.every().day.at('00:40').do(holidays)
#     # schedule.every(10).seconds.do(holidays)
#     while True:
#         schedule.run_pending()

# if __name__ == '__main__':
#     # main()
#     th1 = threading.Thread(target=main, daemon=True)
#     th1.start()
#     # th2 = threading.Thread(target=birthday_add, daemon=True)
#     # th2.start()
#     bot.polling(none_stop=True)

