import unittest
import os
from db import DataBase

class TestDataBase(unittest.TestCase):
    def setUp(self):
        self.db_name = 'test_database.sqlite'
        self.db = DataBase(db_name=self.db_name)

    def tearDown(self):
        self.db.conn.close()
        os.remove(self.db_name)

    def test_insert_value(self):
        self.assertTrue(self.db.insert_value(1, 'token1'))
        self.assertFalse(self.db.insert_value(1, 'token1'))  # Duplicate

    def test_remove_value(self):
        self.db.insert_value(1, 'token1')
        self.assertTrue(self.db.remove_value(1, 'token1'))
        self.assertFalse(self.db.remove_value(1, 'token1'))  # Not found

    def test_get_user_tokens(self):
        self.db.insert_value(1, 'token1')
        self.db.insert_value(1, 'token2')
        tokens = self.db.get_user_tokens(1)
        self.assertIn('token1', tokens)
        self.assertIn('token2', tokens)

    def test_get_users_by_token(self):
        self.db.insert_value(1, 'token1')
        self.db.insert_value(2, 'token1')
        users = self.db.get_users_by_token('token1')
        self.assertIn(1, users)
        self.assertIn(2, users)

if __name__ == '__main__':
    unittest.main()