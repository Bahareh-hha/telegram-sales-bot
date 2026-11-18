import database
database.init_db()
#database.add_product("45000000", "لپتاپ ایسوس")
import csv
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import(
     ApplicationBuilder, CommandHandler,MessageHandler,CallbackQueryHandler,ConversationHandler, filters, ContextTypes
)

PHONE, ADDRES, GET_RECEIPT, GET_PRODUCT_NAME, GET_PRODUCT_PRICE = (
    "PHONE",
"ADDRESS",
"GET_RECEIPT",
"GET_PRODUCT_NAME",
"GET_PRODUCT_PRICE",
)

ADMIN_CHAT_ID = 261601051
TOKEN="9242203333:AAFKqsCOTTLLKz7DsDlc28YYrz4tGQuKDU0"

def get_products_from_csv():
    products_list=[]
    try:
        with open('products.csv', mode='r', encoding='utf-8-sig')as file:
            reader=csv.DictReader(file)
            for row in reader:
                clean_row={key.strip(): value.strip() for key, value in row.items() if key}
                products_list.append(clean_row)
        return products_list
    except Exception as e:
        print(f"خطای خواندن فایلcsv: {e}")
        return[]

def save_order_to_db(user_id, username, product_name, phone, adress):
    try:
        database.add_order(user_id, username, product_name, phone, adress)
        return True
    except Exception as e:
        print(f"خطا در ذخیره سفارش در دیتا بیس: {e}")
        return False

def get_orders_from_csv():
    orders_list =[]
    try:
        with open ('order.csv', mode='r', encoding='utf-8-sig') as file:
            reader=csv.reader(file)
            for row in reader:
                orders_list.append(row)
        return orders_list
    except Exception as e:
        print(f"خطا در خواندن سفارش ها: {e}")
        return[]

    

async def start(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user_name=update.effective_user.first_name

    keyboard=[
        ["مشاهده لیست محصولات 🛍"],
        ["ارتباط با پشتیبانی☎","درباره ما ℹ"]


    ]
    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(f"سلام{user_name} 🌹عزیز! به ربات فروشگاه خوش آمدید_\n لطفا یک گزینه را انتخاب کنید:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=update.message.text
    if "مشاهده لیست محصولات 🛍" in text:
        products=database.get_all_products()
        if not products:
            await update.message.reply_text("در حال حاضر هیج محصولی در انبار یافت نشد ❌")
            return

        await update.message.reply_text("لیست محصولات موجود در انبار:\n\n")
        for item in products:
            name=item.get('name', 'بدون نام')
            price=item.get('price', '0')
            
            prod_id= item.get('id', '0')
            msg=f"🔹{name}\nقیمت 💰: {price} تومان\n📊موجودی: {stock} عدد"
            keyboard=[[InlineKeyboardButton(f"🛒خرید {name}", callback_data=f"buy_{prod_id}_{name}")]]
            reply_markup= InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(msg, reply_markup=reply_markup)

    elif text=="ارتباط با پشتیبانی☎":
        await update.message.reply_text("جهت ارتباط با پشتیبانی با آیدی @support در تماس باشید")
    elif text=="درباره ما ℹ":
        await update.message.reply_text("به فروشگاه آنلاین ما خوش آمدید! ما بهترین کیفیت را ارائه می دهیم")



async def start_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, prod_id, prod_name =query.data.split('_')
    context.user_data['selected_product'] =prod_name

    await query.message.reply_text(f"شما محصول **{prod_name}**را انتخاب کردید.\nلطفا **شماره تماس** خود را وارد کنید: ")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("حالا لطفاّ**آدرس دقیق پستی** خود را ارسال کنید تشکر:")
    return ADDRES

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرآیند ثبت سفارش لغو شد.")
    return ConversationHandler.END

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text

    await update.message.reply_text(
'📍 آدرس شما ثبت شد.\n\nلطفاً تصویر فیش واریزی یا رسید پرداخت خود را'
' ارسال کنید:'
)
    return GET_RECEIPT

async def get_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text(
'لطفاً حتماً تصویر (عکس) فیش واریزی را ارسال کنید:'
)
        return GET_RECEIPT

# دریافت آیدی عکس فیش
    photo_id = update.message.photo[-1].file_id
    user = update.effective_user

    product = context.user_data.get('selected_product', 'نامشخص')
    phone = context.user_data.get('phone', 'نامشخص')
    address = context.user_data.get('address', 'نامشخص')

# ذخیره سفارش در دیتابیس (همان تابعی که از قبل داشتید)
    save_order_to_db(user.id, user.first_name, product, phone, address)

# پیام موفقیت به مشتری
    await update.message.reply_text(
'✅ سفارش و فیش شما با موفقیت ثبت شد!\n\nهمکاران ما به زودی بررسی و با'
' شما تماس خواهند گرفت.'
)

# ارسال عکس و مشخصات کامل برای ادمین
    admin_message = (
    f'🚨 سفارش جدید به همراه فیش واریزی!\n\n📦 محصول: {product}\n📞 تلفن:'
    f' {phone}\n📍 آدرس: {address}\n👤 خریدار: {user.full_name}'
    f' (@{user.username})\n🆔 آیدی کاربر: {user.id}'
)
    await context.bot.send_photo(
chat_id=ADMIN_CHAT_ID, photo=photo_id, caption=admin_message
)

    return ConversationHandler.END

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("شما اجازه دسترسی به این بخش را ندارید.")
        return
    orders= database.get_all_orders()
    if not orders:
        await update.message.reply_text("هنوز سفارشی در سیستم ثبت نشده است")
        return
    text="📋لیست سفارش های ثبت شده در فروشگاه:**\n\n"
    for idx, order in enumerate(orders, 1):
        #[user_id, first_name, product, phone, address]
        if len(order)>=5 :
            text += f"---سفارش شماره {idx} ---\n"
            text +=f"👤نام: {order[1]}\n"
            text +=f"📦محصول: {order[2]}\n"
            text +=f"📞تلفن: {order[3]}\n"
            text +=f"📍آدرس: {order[4]}\n"
    await update.message.reply_text(text)

#شروع فرآیند اضافه کردن محصول توسط ادمین
async def start_add_product(
        update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("شما اجازه دسترسی به این بخش را ندارید.")
        return ConversationHandler.END

    await update.message.reply_text("لطفا نام محصول جدید را وارد کنید (یا برای انصراف cancel\ را بزنید:)")
    return GET_PRODUCT_NAME

async def recive_product_name(
        update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["new_product_name"]=update.message.text
    await update.message.reply_text("حالا قیمت محصول را وارد کنید(فقط به عدد)")
    return GET_PRODUCT_PRICE

async def recive_product_price(
        update: Update, context: ContextTypes.DEFAULT_TYPE
):
    product_name =context.user_data.get("new_product_name")
    product_price = update.message.text

    database.add_product(product_name, product_price)

    
    text=(
            f"محصول{product_name} با قیمت {product_price} تومان باموقیت اضافه شد"
        )
    await update.message.reply_text(text)
    
    return ConversationHandler.END

if __name__=='__main__':
    app=ApplicationBuilder().token(TOKEN).build()

    add_product_handler = ConversationHandler(
        entry_points=[CommandHandler("addproduct", start_add_product)],
        states={
            GET_PRODUCT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recive_product_name)
            ],
            GET_PRODUCT_PRICE:[
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, recive_product_price
                )
            ],

        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(add_product_handler)

    order_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_buy, pattern="^buy_")],
        states={
            PHONE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            GET_RECEIPT: [MessageHandler(filters.PHOTO, get_receipt)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(order_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    app.add_handler(CommandHandler("admin", admin_orders))
    print("ربات همراه با کیبورد روشن شد و آماده ی پاسخگویی است ")
    app.run_polling()
