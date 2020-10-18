from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class BrowseProcessor:

    def __init__(self, db):
        self.db = db
        self.max_no_of_rows_for_objs = 5
        self.file_folder_row_width = 2

    def browse(self, *, chat_id, page, folder_id=None):
        self.chat_id = chat_id
        self.page = int(page)
        if folder_id is None:
            self.folder_id = ""
        else:
            self.folder_id = folder_id
        self.message = self._get_message()
        self.markup = self._get_markup_by_page()
        self.del_markup = self._get_del_markup_by_page()

    def _get_message(self):
        folders = self._get_folder_nms()
        files = self._get_file_nms()
        objs_in_folder = folders + files
        directory = self._get_directory()
        message = f" Directory in: {directory}"
        for obj in objs_in_folder:
            message += "\n \\|\\-" + obj

        return "```" + message + "```"

    def _get_markup_by_page(self):
        markup = InlineKeyboardMarkup()
        top_buttons = self._get_top_buttons()
        obj_buttons = self._get_obj_buttons_by_page()
        del_button = self._get_del_button()
        bottom_buttons = self._get_bottom_buttons_by_page()
        markup.row_width = 3
        markup.add(*top_buttons)
        markup.row_width = self.file_folder_row_width
        markup.add(*obj_buttons)
        markup.row_width = 1
        markup.add(del_button)
        if len(bottom_buttons) > 0:
            markup.row_width = 2
            markup.add(*bottom_buttons)

        return markup

    def _get_del_markup_by_page(self):
        markup = InlineKeyboardMarkup()
        folder_id = self.folder_id
        if self.folder_id is None:
            folder_id = ""
        cancel = InlineKeyboardButton(
            "Cancel",
            callback_data="cancel_" + str(self.page) + "_" + str(folder_id)
        )
        del_obj_buttons = self._get_del_obj_buttons_by_page()
        markup.row(cancel)
        markup.row_width = self.file_folder_row_width
        markup.add(*del_obj_buttons)

        return markup

    def _get_folder_objs(self):
        return self.db.get_child_folders(
            self.chat_id, self.folder_id
        )

    def _get_file_objs(self):
        return self.db.get_files_in_folder(
            self.chat_id, self.folder_id
        )

    def _get_folder_nms(self):
        folder_recs = self._get_folder_objs()
        return [
            "📂" + folder.FOLDER_NM
            for folder in folder_recs
        ]

    def _get_file_nms(self):
        file_recs = self._get_file_objs()
        return [
            "📃" + file.FILE_NM
            for file in file_recs
        ]

    def _is_last_page(self):
        folders = self._get_folder_nms()
        files = self._get_file_nms()
        objs = folders + files
        remaining_buttons = len(objs) - (
            self.max_no_of_rows * self.file_folder_row_width * (self.page - 1)
        )
        buttons_per_page = self.max_no_of_rows * self.file_folder_row_width

        if remaining_buttons > buttons_per_page:
            return False

        return True

    def _get_top_buttons(self):
        top_buttons = []

        if self.folder_id is not None and self.folder_id != "":
            folder_id = str(self.folder_id)
            go_up = InlineKeyboardButton(
                "⬆️Up", callback_data="up_" + str(folder_id)
            )
            top_buttons.append(go_up)
        else:
            folder_id = ""

        top_buttons.extend([
            InlineKeyboardButton("📁Create New Folder",
                                 callback_data="newfold_" + folder_id),
            InlineKeyboardButton("📄Upload File",
                                 callback_data="newfile_" + folder_id)
        ])

        return top_buttons

    def _get_obj_buttons_by_page(self):
        # return obj buttons by page
        max_rows = self.max_no_of_rows_for_objs
        row_width = self.file_folder_row_width
        buttons_per_page = max_rows * row_width

        folder_recs = self._get_folder_objs()
        folder_objs = [
            InlineKeyboardButton("📂" + obj.FOLDER_NM,
                                 callback_data="fold_" + str(obj.FOLDER_ID))
            for obj in folder_recs
        ]

        file_recs = self._get_file_objs()
        file_objs = [
            InlineKeyboardButton("📃" + obj.FILE_NM,
                                 callback_data="file_" +
                                 str(obj.MESSAGE_ID))
            for obj in file_recs
        ]

        buttons = folder_objs + file_objs
        i = (buttons_per_page * self.page) - buttons_per_page
        j = (buttons_per_page * self.page)

        return buttons[i:j]

    def _get_del_button(self):
        return InlineKeyboardButton(
                "❌Delete",
                callback_data="del_" + str(self.page) +
                "_" + str(self.folder_id)
            )

    def _get_bottom_buttons_by_page(self):
        # return last row buttons by page
        bottom_buttons = []
        folder_id = str(self.folder_id)
        if folder_id is None:
            folder_id = ""
        if self.page > 1:
            prev_page = InlineKeyboardButton(
                            "◀️" + str(self.page - 1),
                            callback_data="prev_" + str(self.page - 1) +
                            "_" + folder_id
                        )
            bottom_buttons.append(prev_page)
        folders = self._get_folder_nms()
        files = self._get_file_nms()
        folder_objs = folders + files
        max_rows = self.max_no_of_rows_for_objs
        row_width = self.file_folder_row_width
        page = self.page
        prev_and_current_buttons = max_rows * row_width * page
        if prev_and_current_buttons < len(folder_objs):
            next_page = InlineKeyboardButton(
                            str(self.page + 1) + "▶️",
                            callback_data="next_" + str(self.page + 1) +
                            "_" + folder_id
                        )
            bottom_buttons.append(next_page)
        return bottom_buttons

    def _get_del_obj_buttons_by_page(self):
        # return obj buttons by page
        max_rows = self.max_no_of_rows_for_objs
        row_width = self.file_folder_row_width
        buttons_per_page = max_rows * row_width
        folder_id = str(self.folder_id)
        if folder_id is None:
            folder_id = ""

        folder_recs = self._get_folder_objs()
        folder_objs = [
            InlineKeyboardButton("❌📂" + obj.FOLDER_NM,
                                 callback_data="delfold_" +
                                 str(obj.FOLDER_ID) +
                                 "_" + str(self.page) +
                                 "_" + folder_id)
            for obj in folder_recs
        ]

        file_recs = self._get_file_objs()
        file_objs = [
            InlineKeyboardButton("❌📃" + obj.FILE_NM,
                                 callback_data="delfile_" +
                                 str(obj.FILE_ID) +
                                 "_" + str(self.page) +
                                 "_" + folder_id)
            for obj in file_recs
        ]

        buttons = folder_objs + file_objs
        i = (buttons_per_page * self.page) - buttons_per_page
        j = (buttons_per_page * self.page)

        return buttons[i:j]

    def _get_directory(self):
        directory = "/"
        folder_id = self.folder_id
        while True:
            if folder_id == "" or folder_id is None:
                break
            else:
                folder_rec = self.db.get_folder_nm_by_id(folder_id)
                folder_nm = "/" + folder_rec[0].FOLDER_NM
                folder_id = folder_rec[0].PARENT_FLDR_ID
                directory = folder_nm + directory

        return directory
