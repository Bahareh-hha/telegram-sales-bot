import sqlite3


def init_db():
  connection = sqlite3.connect("store.db")
  cursor = connection.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price TEXT NOT NULL
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            product_name TEXT,
            phone TEXT,
            address TEXT
        )
    """)

  connection.commit()
  connection.close()


def add_product(name, price):
  """اضافه کردن محصول جدید به دیتابیس"""
  connection = sqlite3.connect("store.db")
  cursor = connection.cursor()
  cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
  connection.commit()
  connection.close()


def get_all_products():
  """خواندن محصولات از دیتابیس به صورت لیست دیکشنری"""
  connection = sqlite3.connect("store.db")
  connection.row_factory = sqlite3.Row  # برای دسترسی به ستون‌ها با نام
  cursor = connection.cursor()
  cursor.execute("SELECT id, name, price FROM products")
  rows = cursor.fetchall()

  products_list = []
  for row in rows:
    products_list.append({
        "id": row["id"],
        "name": row["name"],
        "price": row["price"],
        "stock": "موجود",  # مقدار پیش‌فرض برای موجودی
    })

  connection.close()
  return products_list


def add_order(user_id, username, product_name, phone, address):
  connection = sqlite3.connect("store.db")
  cursor = connection.cursor()
  cursor.execute(
      "INSERT INTO orders (user_id, username, product_name, phone, address)"
      " VALUES (?, ?, ?, ?, ?)",
      (user_id, username, product_name, phone, address),
  )
  connection.commit()
  connection.close()


def get_all_orders():
  connection = sqlite3.connect("store.db")
  connection.row_factory = sqlite3.Row
  cursor = connection.cursor()
  cursor.execute(
      "SELECT user_id, username, product_name, phone, address FROM orders"
  )
  orders = cursor.fetchall()
  connection.close()
  return orders


def delete_product(product_id):
  conn = sqlite3.connect("store.db")
  cursor = conn.cursor()
  # فرض بر این است که نام جدول شما products و ستون شناسه id است
  cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
  conn.commit()
  conn.close()