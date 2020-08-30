import sqlite3


class DbHelper:

    def __init__(self, db_name):

        self.db_name = db_name
        self.connect()

    def connect(self):

        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row

    def insert_folder(self, chat_id, folder_nm, parent_fldr_id):

        self.connect()
        sql = "INSERT INTO FOLDER (CHAT_ID, FOLDER_NM, PARENT_FLDR_ID) \
               VALUES (?, ?, ?)"
        self.conn.execute(sql, (chat_id, folder_nm, parent_fldr_id))
        self.conn.commit()

    def update_folder_name(self, id, new_folder_nm):

        self.connect()
        sql = "UPDATE FOLDER \
                  SET FOLDER_NM = ? \
                WHERE rowid = ?"
        self.conn.execute(sql, (new_folder_nm, id))
        self.conn.commit()

    def delete_folder_rec(self, folder_id):

        self.connect()
        delete_files = "DELETE FROM FILE \
                        WHERE folder_id = ?"
        delete_child_folders = "DELETE FROM FOLDER \
                                WHERE parent_fldr_id = ?"
        delete_folder = "DELETE FROM FOLDER \
                         WHERE rowid = ?"
        self.conn.execute(delete_files, (folder_id,))
        self.conn.execute(delete_child_folders, (folder_id,))
        self.conn.execute(delete_folder, (folder_id,))
        self.conn.commit()

    def insert_file(self, message, folder_id):

        self.connect()
        chat_id = message.chat.id
        message_id = message.message_id
        file_nm = message.document.file_name

        sql = "INSERT INTO FILE (CHAT_ID, MESSAGE_ID, FILE_NM, FOLDER_ID) \
               VALUES (?, ?, ?, ?)"
        self.conn.execute(sql, (chat_id, message_id, file_nm, folder_id))
        self.conn.commit()

    def update_file_nm(self, id, new_file_nm):

        self.connect()
        sql = "UPDATE FILE \
                  SET FILE_NM = ? \
                WHERE rowid = ?"
        self.conn.execute(sql, (new_file_nm, id))
        self.conn.commit()

    def delete_file_rec(self, file_id):

        self.connect()
        sql = "DELETE FROM FILE \
               WHERE rowid = ?"
        self.conn.execute(sql, (file_id,))
        self.conn.commit()

    def get_child_folders(self, chat_id, parent_fldr_id=None):

        self.connect()
        sql = "SELECT rowid, FOLDER_NM \
                 FROM FOLDER \
                WHERE CHAT_ID = ? \
                  AND PARENT_FLDR_ID = ? \
               ORDER BY FOLDER_NM"
        cur = self.conn.cursor()
        cur.execute(sql, (chat_id, parent_fldr_id))
        return cur.fetchall()

    def get_files_in_folder(self, chat_id, folder_id=None):

        self.connect()
        sql = "SELECT rowid, FILE_NM, MESSAGE_ID \
                 FROM FILE \
                WHERE CHAT_ID = ? \
                  AND FOLDER_ID = ? \
               ORDER BY FILE_NM"
        cur = self.conn.cursor()
        cur.execute(sql, (chat_id, folder_id))
        return cur.fetchall()

    def get_folder_nm_by_id(self, folder_id):

        self.connect()
        sql = "SELECT FOLDER_NM, PARENT_FLDR_ID \
                 FROM FOLDER \
                WHERE rowid = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (folder_id,))
        return cur.fetchall()

    def get_parent_of_folder(self, folder_id):

        self.connect()
        sql = "SELECT PARENT_FLDR_ID \
                 FROM FOLDER \
                WHERE rowid = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (folder_id,))
        return cur.fetchall()
