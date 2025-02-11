import sqlite3
import os

DB_PATH = "users.db"

def delete_db():
    """Удаляет базу данных, если она существует"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️ База данных {DB_PATH} удалена.")
    else:
        print("✅ База данных отсутствует, удалять не нужно.")

def init_db():
    """Создаёт таблицу, если её нет"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            cosmos_address TEXT,
            injective_address TEXT,
            celestia_address TEXT,
            dydx_address TEXT
        )''')
        conn.commit()

def save_address(user_id: int, address: str, network: str):
    """Сохраняет адрес пользователя"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        column = f"{network}_address"  # Определяем нужный столбец
        cursor.execute(f"INSERT INTO users (user_id, {column}) VALUES (?, ?) "
                       f"ON CONFLICT(user_id) DO UPDATE SET {column}=?",
                       (user_id, address, address))
        conn.commit()

def get_address(user_id: int, network: str) -> str:
    """Возвращает адрес пользователя, или None, если его нет"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        column = f"{network}_address"
        cursor.execute(f"SELECT {column} FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()

        if row and row[0]:  # Проверяем, что row не None и содержит адрес
            return row[0].strip()
        else:
            return None  # Возвращаем None, если адрес отсутствует
