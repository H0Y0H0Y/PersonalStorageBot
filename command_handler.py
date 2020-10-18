from BrowseProcessor import BrowseProcessor
from db_handler import DbHelper

db = DbHelper()
processor = BrowseProcessor(db)


def process_browse(bot, message):
    chat_id = message.chat.id
    processor.browse(chat_id=chat_id, page=1)

    bot.send_message(
        chat_id=chat_id,
        parse_mode='MarkdownV2',
        text=processor.message,
        reply_markup=processor.markup
    )
