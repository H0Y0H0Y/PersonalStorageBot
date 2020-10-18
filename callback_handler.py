from telebot.types import ForceReply

from BrowseProcessor import BrowseProcessor
from db_handler import DbHelper

db = DbHelper()
processor = BrowseProcessor(db)


# first row buttons
def go_up(bot, query, current_folder_id):
    # navigate to parent directory
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    folder_id_of_parent = db.get_parent_of_folder(current_folder_id)
    folder_id = folder_id_of_parent[0].PARENT_FLDR_ID
    display_folder_contents(bot, chat_id, page=1,
                            folder_id=folder_id,
                            message_id=message_id)


def create_new_folder(bot, query, current_folder_id):
    # create new folder obj
    if current_folder_id == "":
        current_folder_id = None
    msg = "Creating a new folder in the directory.\n \
        Please send me the name of the new folder."
    message = bot.send_message(
        chat_id=query.message.chat.id,
        text=msg,
        reply_markup=ForceReply(selective=False)
    )
    bot.register_next_step_handler(message, process_create_folder,
                                   current_folder_id, bot)


def process_create_folder(message, folder_id, bot):
    chat_id = message.chat.id

    if message.text is None or message.text == "":
        message = bot.send_message(
            chat_id=chat_id,
            text="Please send me the name of the new folder.",
            reply_markup=ForceReply(selective=False)
        )
        bot.register_next_step_handler(message, process_create_folder,
                                       folder_id, bot)

    # add exception handling here
    db.insert_folder(message.chat.id, message.text, folder_id)

    bot.send_message(
        chat_id=chat_id,
        text="Folder created."
    )
    display_folder_contents(bot, chat_id, page=1, folder_id=folder_id)


def display_folder_contents(bot, chat_id, *, page, folder_id, message_id=None):
    processor.browse(chat_id=chat_id, page=page, folder_id=folder_id)
    if message_id is None:
        bot.send_message(
            chat_id=chat_id,
            text=processor.message,
            reply_markup=processor.markup,
            parse_mode="MarkdownV2"
        )
    else:
        bot.edit_message_text(
            chat_id=chat_id,
            text=processor.message,
            message_id=message_id,
            reply_markup=processor.markup,
            parse_mode="MarkdownV2"
        )


def display_page_for_delete(bot, chat_id, message_id, *, page, folder_id):
    processor.browse(chat_id=chat_id, page=page, folder_id=folder_id)
    bot.edit_message_text(
        chat_id=chat_id,
        text=processor.message,
        message_id=message_id,
        reply_markup=processor.del_markup,
        parse_mode="MarkdownV2"
    )


def upload_file(bot, query, current_folder_id):
    # ask for file to upload and link to the current folder
    if current_folder_id == "":
        current_folder_id = None
    message = bot.send_message(
        chat_id=query.message.chat.id,
        text="Upload a file to this folder.",
        reply_markup=ForceReply(selective=False)
    )
    bot.register_next_step_handler(message, process_uploaded_file,
                                   current_folder_id, bot)


def process_uploaded_file(message, folder_id, bot):
    # insert filename and folder the file will be placed into
    chat_id = message.chat.id

    if message.document is None:
        message = bot.send_message(
            chat_id=chat_id,
            text="I can only accept a file."
        )

    else:
        # Add exception handling here
        db.insert_file(message, folder_id)

        display_folder_contents(bot, chat_id, page=1, folder_id=folder_id)


# buttons for objs in folder
def go_to_folder(bot, query, browse_to_folder_id):
    # navigate to selected folder
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    display_folder_contents(bot, chat_id, page=1,
                            folder_id=browse_to_folder_id,
                            message_id=message_id)


def delete_object(bot, query, page, folder_id):
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    display_page_for_delete(bot, chat_id, message_id, page=page,
                            folder_id=folder_id)


def get_file(bot, query, message_id):
    # forward the message with the selected file
    chat_id = query.message.chat.id
    bot.forward_message(
        chat_id=chat_id,
        from_chat_id=chat_id,
        message_id=message_id
    )


# navigation buttons
def go_to_page(bot, query, page, current_folder_id):
    # go to specified page
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    display_folder_contents(bot, chat_id, page=page,
                            folder_id=current_folder_id,
                            message_id=message_id)


# cancel button
def cancel_delete(bot, query, page, folder_id):
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    display_folder_contents(bot, chat_id, page=page,
                            folder_id=folder_id,
                            message_id=message_id)


def delete_folder(bot, query, del_folder_id, page, current_folder_id):
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    db.delete_folder_rec(del_folder_id)
    display_page_for_delete(bot, chat_id, message_id, page=page,
                            folder_id=current_folder_id)


def delete_file(bot, query, del_file_id, page, current_folder_id):
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    db.delete_file_rec(del_file_id)
    display_page_for_delete(bot, chat_id, message_id, page=page,
                            folder_id=current_folder_id)
