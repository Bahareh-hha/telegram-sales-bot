import os
import sqlite3

# بررسی اینکه آیا دیتابیس ابری (پستگرس) روی سرور فعال است یا خیر
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        # اتصال به دیتابیس ابری PostgreSQL در رندر
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn, "postgres"
    else:
        # اتصال به دیتابیس محلی SQLite روی سیستم
        conn = sqlite3.connect("store.db")
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

def init_db():
    """ساخت جداول دیتابیس در صورت عدم وجود"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    if db_type == "postgres":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                price TEXT NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                username TEXT,
                product_name TEXT,
                phone TEXT,
                address TEXT
            );
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price TEXT NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                product_name TEXT,
                phone TEXT,
                address TEXT
            );
        """)
        
    conn.commit()
    conn.close()

def add_product(name, price):
    """اضافه کردن محصول جدید به دیتابیس"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == "postgres":
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s)", (name, price))
    else:
        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()

def get_all_products():
    """خواندن تمام محصولات از دیتابیس به صورت دیکشنری"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products")
    
    products_list = []
    if db_type == "postgres":
        rows = cursor.fetchall()
        for row in rows:
            products_list.append({
                "id": row[0],
                "name": row[1],
                "price": row[2],
                "stock": "موجود"
            })
    else:
        rows = cursor.fetchall()
        for row in rows:
            products_list.append({
                "id": row["id"],
                "name": row["name"],
                "price": row["price"],
                "stock": "موجود"
            })
            
    conn.close()
    return products_list

def add_order(user_id, username, product_name, phone, address):
    """ثبت سفارش جدید در دیتابیس"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == "postgres":
        cursor.execute(
            "INSERT INTO orders (user_id, username, product_name, phone, address) VALUES (%s, %s, %s, %s, %s)",
            (user_id, username, product_name, phone, address)
        )
    else:
        cursor.execute(
            "INSERT INTO orders (user_id, username, product_name, phone, address) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, product_name, phone, address)
        )
    conn.commit()
    conn.close()

def get_all_orders():
    """خواندن لیست سفارش‌ها"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, product_name, phone, address FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return orders
def delete_product(product_id):
    """حذف محصول بر اساس شناسه"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == "postgres":
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    else:
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
