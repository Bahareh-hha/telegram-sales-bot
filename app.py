import os
from database import (
    add_product,
    delete_product,
    get_all_orders,
    get_all_products,
    init_db,
)
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
init_db()

@app.route("/", methods=["GET", "POST"])
def home():
  if request.method == "POST":
    product_name = request.form.get("name")
    product_price = request.form.get("price")

    if product_name and product_price:
      add_product(product_name, product_price)

    return redirect(url_for("home"))

  products = get_all_products()
  orders = get_all_orders()  # گرفتن سفارش‌ها از دیتابیس

  html = """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>پنل مدیریت فروشگاه و سفارش‌ها</title>
        <style>
            body { font-family: Tahoma, sans-serif; background-color: #f4f7f6; padding: 20px; }
            .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h2, h3 { color: #333; }
            form { background: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 20px; }
            input { padding: 8px; width: 35%; margin-left: 10px; border: 1px solid #ccc; border-radius: 4px; }
            button { padding: 8px 15px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #218838; }
            .delete-btn { background: #dc3545; padding: 4px 10px; font-size: 14px; text-decoration: none; border-radius: 4px; color: white; }
            .delete-btn:hover { background: #c82333; }
            ul { padding-right: 20px; }
            li { margin-bottom: 10px; font-size: 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 6px; }
            .section-box { background: #fff; padding: 15px 20px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 25px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🛠 پنل مدیریت مرکزی فروشگاه</h2>
            <hr>
            
            <div class="section-box">
                <h3>➕ افزودن محصول جدید به انبار</h3>
                <form method="POST">
                    <input type="text" name="name" placeholder="نام محصول" required>
                    <input type="text" name="price" placeholder="قیمت (تومان)" required>
                    <button type="submit">ثبت در انبار</button>
                </form>
            </div>

            <div class="section-box">
                <h3>📦 لیست محصولات موجود</h3>
                <ul>
    """

  for p in products:
    html += f"<li><span><b>{p['name']}</b> - قیمت: {p['price']} تومان</span> <a href='/delete/{p['id']}' class='delete-btn'>حذف</a></li>"

  html += """
                </ul>
            </div>

            <div class="section-box">
                <h3>🛍 لیست سفارش‌های ثبت‌شده از طریق ربات</h3>
                <ul>
    """

  try:
    if orders:
      for o in orders:
        html += f"<li><span>مشتری: <b>{o['username']}</b> | محصول: <b>{o['product_name']}</b> | تلفن: {o['phone']} | آدرس: {o['address']}</span></li>"
    else:
      html += "<li>هنوز هیچ سفارشی ثبت نشده است.</li>"
  except Exception:
    html += "<li>خطا در خواندن سفارش‌ها.</li>"

  html += """
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
  return html


@app.route("/delete/<int:product_id>")
def delete(product_id):
  delete_product(product_id)
  return redirect(url_for("home"))


if __name__ == "__main__":
  port= int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
