def update_game_location(barcode, bookcase, shelf):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            UPDATE games SET bookcase = ?, shelf = ? WHERE barcode = ?;
        ''', (bookcase, shelf, barcode))
        conn.commit()
def list_loaned_games():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('SELECT name, barcode, bookcase, shelf, loaned_to, description, image_url FROM games WHERE loaned_to IS NOT NULL')
        return cursor.fetchall()
import sqlite3

DB_FILE = 'games.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                barcode TEXT UNIQUE,
                bookcase TEXT,
                shelf TEXT,
                loaned_to TEXT,
                description TEXT,
                image_url TEXT
            );
        ''')
        conn.commit()

def add_game(name, barcode, bookcase, shelf, description=None, image_url=None):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            INSERT OR REPLACE INTO games (name, barcode, bookcase, shelf, loaned_to, description, image_url)
            VALUES (?, ?, ?, ?, NULL, ?, ?);
        ''', (name, barcode, bookcase, shelf, description, image_url))
        conn.commit()
def get_game_by_barcode(barcode):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('''
            SELECT name, barcode, bookcase, shelf, loaned_to, description, image_url FROM games WHERE barcode = ?
        ''', (barcode,))
        return cursor.fetchone()

def delete_game(barcode):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            DELETE FROM games WHERE barcode = ?;
        ''', (barcode,))
        conn.commit()

def loan_game(barcode, person):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            UPDATE games SET loaned_to = ? WHERE barcode = ?;
        ''', (person, barcode))
        conn.commit()

def return_game(barcode):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            UPDATE games SET loaned_to = NULL WHERE barcode = ?;
        ''', (barcode,))
        conn.commit()

def list_games():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('SELECT name, barcode, bookcase, shelf, loaned_to, description, image_url FROM games')
        return cursor.fetchall()
