import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, Response
from threading import Thread
import logging
import os
from dotenv import load_dotenv  # برای امنیت رمز ها
load_dotenv()

# توکن‌های ربات و API انس جهانی
API_TOKEN = os.getenv("7429159046:AAEjupyyhS7y1NfHPwkr71OGLsCGawFPSsU")

GOLDAPI_KEY = os.getenv("goldapi-3v4m1smawx0q3m-io")


# تنظیم لاگ‌ها برای دیباگ و بررسی وضعیت ربات
logging.basicConfig(
    format='%(name)s - %(asctime)s - %(levelname)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# چت آی‌دی شما برای تست ارسال روزانه
MY_CHAT_ID = 123456789  # عددی که باید جایگزین کنی با چت‌آی‌دی خودت

# گرفتن قیمت انس طلا یا نقره به دلار


def get_price(metal_code):
    url = f"https://www.goldapi.io/api/{metal_code}/USD"
    headers = {
        "x-access-token": GOLDAPI_KEY,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("price")
    else:
        return None

# گرفتن نرخ دلار به تومان (از API آزاد یا عدد ثابت تستی)


def get_usd_to_irr_rate():
    # در نسخه واقعی این مقدار رو از یک API نرخ ارز بگیر
    return 55000  # نرخ فرضی: هر دلار = 55000 تومان

# تبدیل قیمت دلار به تومان


def convert_to_toman(usd_price):
    return round(usd_price * get_usd_to_irr_rate())

# هندلر دستور /start با منو


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['طلا', 'نقره']]  # دکمه‌ها
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("سلام! قیمت چی رو می‌خوای؟", reply_markup=reply_markup)

# بررسی پیام‌های متنی کاربر و تشخیص نوع فلز


async def metal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    gold_words = ['طلا', 'gold']
    silver_words = ['نقره', 'silver']

    if text in gold_words:
        price = get_price("XAU")
        if price:
            toman = convert_to_toman(price)
            await update.message.reply_text(f"قیمت طلا:\n{price} دلار\n{toman:,} تومان")
        else:
            await update.message.reply_text("خطا در دریافت قیمت طلا.")
    elif text in silver_words:
        price = get_price("XAG")
        if price:
            toman = convert_to_toman(price)
            await update.message.reply_text(f"قیمت نقره:\n{price} دلار\n{toman:,} تومان")
        else:
            await update.message.reply_text("خطا در دریافت قیمت نقره.")
    else:
        await update.message.reply_text("لطفاً فقط بنویس: طلا یا نقره.")

# اجرای فلask برای فعال موندن در render
flask_app = Flask('')


@flask_app.route('/')
def home():
    return "ربات فعال است!"


@flask_app.route('/', methods=['HEAD'])
def head():
    return Response(status=200)


def run():

    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()

# ارسال قیمت روزانه (می‌تونی این رو از cronjob در Render بزنی روی /daily_price)


@flask_app.route('/daily_price')
def daily_price():
    gold = get_price("XAU")
    silver = get_price("XAG")

    if gold and silver:
        gold_toman = convert_to_toman(gold)
        silver_toman = convert_to_toman(silver)
        msg = f"قیمت روز:\n\nطلا: {gold} دلار / {gold_toman:,} تومان\nنقره: {silver} دلار / {silver_toman:,} تومان"
    else:
        msg = "خطا در دریافت قیمت روزانه."

    requests.get(f"https://api.telegram.org/bot{API_TOKEN}/sendMessage", params={
        "chat_id": MY_CHAT_ID,
        "text": msg
    })

    return "ok"


# اجرای ربات
if __name__ == '__main__':
    keep_alive()  # روشن نگه داشتن سرور
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))

    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, metal_handler))

    app.run_polling()


print("Bot is working")
