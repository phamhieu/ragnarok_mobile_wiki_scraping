import logging
import os
import sqlite3


class Monster(object):
    name = ''
    url = ''
    level = 0
    hp = 0
    base_ex = 0
    job_ex = 0

class DbManager(object):
    def __init__(self):
        self.db_dir = os.path.join(os.path.dirname(__file__), '../resources/database/scraping_v1.db')
        self.create_tables();

    def create_tables(self):
        db = sqlite3.connect(self.db_dir)
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monsters(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT, level INTEGER,  
                hp INTEGER, base_ex INTEGER, job_ex INTEGER)
        ''')

        db.close()

    def insert_monster(self, monster):
        if monster is None:
            return

        try:
            db = sqlite3.connect(self.db_dir)
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO monsters(name, url, level, hp, base_ex, job_ex) 
                VALUES(?,?,?,?,?,?)
            ''', (monster.name, monster.url, monster.level, monster.hp, monster.base_ex, monster.job_ex)
            )
            db.commit()
        # Catch the exception
        except Exception as e:
            # Roll back any change if something goes wrong
            db.rollback()
            raise e
        finally:
            # Close the db connection
            db.close()