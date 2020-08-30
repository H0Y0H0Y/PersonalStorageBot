import configparser
import logging

import telebot

from command_handler import process_browse
import callback_handler


config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('DEFAULT', 'token')
bot = telebot.TeleBot(token)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


@bot.message_handler(commands=['getChatId'])
def get_chat_id(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, chat_id)


@bot.message_handler(commands=['browse'])
def browse(message):
    process_browse(bot, message)


@bot.callback_query_handler(func=lambda query: True)
def callback_query_processor(query):
    data = query.data.split('_')
    value = data[1]
    # first row buttons
    if data[0] == "up":
        callback_handler.go_up(bot, query, value)
    if data[0] == "newfold":
        callback_handler.create_new_folder(bot, query, value)
    if data[0] == "newfile":
        callback_handler.upload_file(bot, query, value)

    # buttons for objects in folder
    if data[0] == "fold":
        callback_handler.go_to_folder(bot, query, value)
    if data[0] == "file":
        callback_handler.get_file(bot, query, value)

    # delete button
    if data[0] == "del":
        page = value
        folder_id = data[2]
        callback_handler.delete_object(bot, query, page, folder_id)

    # navigation buttons
    if data[0] in ["prev", "next"]:
        folder_id = data[2]
        callback_handler.go_to_page(bot, query, value, folder_id)

    # delete buttons
    if data[0] == "cancel":
        page = value
        folder_id = data[2]
        callback_handler.cancel_delete(bot, query, page, folder_id)
    if data[0] == "delfold":
        page = data[2]
        current_folder_id = data[3]
        callback_handler.delete_folder(bot, query, value, page,
                                       current_folder_id)
    if data[0] == "delfile":
        page = data[2]
        current_folder_id = data[3]
        callback_handler.delete_file(bot, query, value, page,
                                     current_folder_id)


if __name__ == '__main__':
    bot.polling(none_stop=True)
