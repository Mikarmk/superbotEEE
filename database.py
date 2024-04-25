import sqlite3
from typing import Tuple, List

def create_database() -> None:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS files
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  chat_id INTEGER, 
                  file_type TEXT, 
                  file_id TEXT, 
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()

def save_file_info(chat_id: int, file_type: str, file_id: str) -> None:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("INSERT INTO files (chat_id, file_type, file_id) VALUES (?, ?, ?)", (chat_id, file_type, file_id))
    conn.commit()
    conn.close()

def get_user_files(chat_id: int) -> List[Tuple[str, str, str]]:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT file_type, file_id, timestamp FROM files WHERE chat_id = ?", (chat_id,))
    files = c.fetchall()
    conn.close()

    return files
