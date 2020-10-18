import configparser

import mariadb

config = configparser.ConfigParser()
config.read('config.ini')
conn_dict = {
    'USER': config.get('DATABASE', 'USER'),
    'PASSWORD': config.get('DATABASE', 'PASSWORD'),
    'HOST': config.get('DATABASE', 'HOST'),
    'PORT': config.get('DATABASE', 'PORT'),
    'DATABASE': config.get('DATABASE', 'DB')
}


class DbHelper:

    def __init__(self, conn_dict=conn_dict):

        self.user = conn_dict.get('USER')
        self.password = conn_dict.get('PASSWORD')
        self.host = conn_dict.get('HOST')
        self.port = int(conn_dict.get('PORT'))
        self.database = conn_dict.get('DATABASE')

    def connect(self):

        try:
            self.conn = mariadb.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database
            )
        except mariadb.Error as e:
            print(f"Error connecting to db: {e}")

    def close(self):

        self.conn.close()

    def insert_folder(self, chat_id, folder_nm, parent_fldr_id):

        self.connect()
        cur = self.conn.cursor()
        sql = "INSERT INTO FOLDER (CHAT_ID, FOLDER_NM, PARENT_FLDR_ID) \
               VALUES (?, ?, ?)"
        cur.execute(sql, (chat_id, folder_nm, parent_fldr_id))
        # if parent_fldr_id:
        #     sql = "INSERT INTO FOLDER (CHAT_ID, FOLDER_NM, PARENT_FLDR_ID) \
        #            VALUES (?, ?, ?)"
        #     cur.execute(sql, (chat_id, folder_nm, parent_fldr_id))
        # else:
        #     sql = "INSERT INTO FOLDER (CHAT_ID, FOLDER_NM) \
        #            VALUES (?, ?)"
        #     cur.execute(sql, (chat_id, folder_nm))
        self.conn.commit()

    def update_folder_name(self, id, new_folder_nm):

        self.connect()
        cur = self.conn.cursor()
        sql = "UPDATE FOLDER \
                  SET FOLDER_NM = ? \
                WHERE FOLDER_ID = ?"
        cur.execute(sql, (new_folder_nm, id))
        self.conn.commit()
        self.close()

    def delete_folder_rec(self, folder_id):

        self.connect()
        cur = self.conn.cursor()
        delete_files = "DELETE FROM FILE \
                        WHERE folder_id = ?"
        delete_child_folders = "DELETE FROM FOLDER \
                                WHERE parent_fldr_id = ?"
        delete_folder = "DELETE FROM FOLDER \
                         WHERE FOLDER_ID = ?"
        cur.execute(delete_files, (folder_id,))
        cur.execute(delete_child_folders, (folder_id,))
        cur.execute(delete_folder, (folder_id,))
        self.conn.commit()
        self.close()

    def insert_file(self, message, folder_id):

        self.connect()
        cur = self.conn.cursor()
        chat_id = message.chat.id
        message_id = message.message_id
        file_nm = message.document.file_name

        sql = "INSERT INTO FILE (CHAT_ID, MESSAGE_ID, FILE_NM, FOLDER_ID) \
               VALUES (?, ?, ?, ?)"
        cur.execute(sql, (chat_id, message_id, file_nm, folder_id))
        self.conn.commit()
        self.close()

    def update_file_nm(self, id, new_file_nm):

        self.connect()
        cur = self.conn.cursor()
        sql = "UPDATE FILE \
                  SET FILE_NM = ? \
                WHERE FILE_ID = ?"
        cur.execute(sql, (new_file_nm, id))
        self.conn.commit()
        self.close

    def delete_file_rec(self, file_id):

        self.connect()
        cur = self.conn.cursor()
        sql = "DELETE FROM FILE \
               WHERE FILE_ID = ?"
        cur.execute(sql, (file_id,))
        self.conn.commit()
        self.close

    def get_child_folders(self, chat_id, parent_fldr_id=None):

        if parent_fldr_id == "":
            parent_fldr_id = None
        self.connect()
        sql = "SELECT FOLDER_ID, FOLDER_NM \
                 FROM FOLDER \
                WHERE CHAT_ID = ? \
                  AND PARENT_FLDR_ID <=> ? \
               ORDER BY FOLDER_NM"
        cur = self.conn.cursor(named_tuple=True)
        cur.execute(sql, (chat_id, parent_fldr_id))
        rows = cur.fetchall()
        self.close()
        return rows

    def get_files_in_folder(self, chat_id, folder_id=None):

        if folder_id == "":
            folder_id = None
        self.connect()
        sql = "SELECT FILE_ID, FILE_NM, MESSAGE_ID \
                 FROM FILE \
                WHERE CHAT_ID = ? \
                  AND FOLDER_ID <=> ? \
               ORDER BY FILE_NM"
        cur = self.conn.cursor(named_tuple=True)
        cur.execute(sql, (chat_id, folder_id))
        rows = cur.fetchall()
        self.close()
        return rows

    def get_folder_nm_by_id(self, folder_id):

        self.connect()
        sql = "SELECT FOLDER_NM, PARENT_FLDR_ID \
                 FROM FOLDER \
                WHERE FOLDER_ID = ?"
        cur = self.conn.cursor(named_tuple=True)
        cur.execute(sql, (folder_id,))
        rows = cur.fetchall()
        self.close()
        return rows

    def get_parent_of_folder(self, folder_id):

        self.connect()
        sql = "SELECT PARENT_FLDR_ID \
                 FROM FOLDER \
                WHERE FOLDER_ID = ?"
        cur = self.conn.cursor(named_tuple=True)
        cur.execute(sql, (folder_id,))
        rows = cur.fetchall()
        self.close()
        return rows
