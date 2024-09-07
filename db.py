import sqlite3
import os

class DataBase:
    def __init__(self, db_name='bot_database.sqlite'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.initialize_db()

    def initialize_db(self):
        db_exists = os.path.exists(self.db_name)
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        if not db_exists:
            self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                userId INTEGER,
                token TEXT,
                PRIMARY KEY (userId, token)
            )
        ''')
        self.conn.commit()

    def insert_value(self, user_id, token):
        try:
            self.cursor.execute('INSERT INTO Users (userId, token) VALUES (?, ?)', (user_id, token))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Record already exists

    def remove_value(self, user_id, token):
        self.cursor.execute('DELETE FROM Users WHERE userId = ? AND token = ?', (user_id, token))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_user_tokens(self, user_id):
        self.cursor.execute('SELECT token FROM Users WHERE userId = ?', (user_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def __del__(self):
        if self.conn:
            self.conn.close()
