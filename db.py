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
                loaned_to TEXT
            );
        ''')
        conn.commit()

def add_game(name, barcode, bookcase, shelf):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            INSERT OR REPLACE INTO games (name, barcode, bookcase, shelf, loaned_to)
            VALUES (?, ?, ?, ?, NULL);
        ''', (name, barcode, bookcase, shelf))
        conn.commit()

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
        cursor = conn.execute('SELECT name, barcode, bookcase, shelf, loaned_to FROM games')
        return cursor.fetchall()
