import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, Response
from threading import Thread
import logging
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
GOLDAPI_KEY = os.getenv("GOLDAPI_KEY")
MY_CHAT_ID = ("@B2023KAB")
logging.basicConfig(level=logging.INFO)

# ==================== Flask ====================

flask_app = Flask('')


@flask_app.route('/')
def home():
    return "ربات فعال است!"


@flask_app.route('/', methods=['HEAD'])
def head():
    return Response(status=200)


def run():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()

# ==================== Gold API ====================


def get_price(metal_code):  # XAU یا XAG
    url = f"https://www.goldapi.io/api/{metal_code}/USD"
    headers = {
        "x-access-token": GOLDAPI_KEY,
        "Content-Type": "application/json"
    }
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.json().get("price")
    except:
        pass
    return None


def get_usd_to_irr_rate():
    return 83000  # نرخ فرضی


def convert_to_toman(usd_price):
    return round(usd_price * get_usd_to_irr_rate())

# ==================== Telegram Handlers ====================


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['طلا', 'نقره']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("سلام! قیمت چی رو می‌خوای؟", reply_markup=reply_markup)


async def metal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if text in ['طلا', 'gold']:
        price = get_price("XAU")
        if price:
            toman = convert_to_toman(price)
            await update.message.reply_text(f"قیمت طلا:\n{price} دلار\n{toman:,} تومان")
        else:
            await update.message.reply_text("دریافت قیمت طلا ممکن نیست.")
    elif text in ['نقره', 'silver']:
        price = get_price("XAG")
        if price:
            toman = convert_to_toman(price)
            await update.message.reply_text(f"قیمت نقره:\n{price} دلار\n{toman:,} تومان")
        else:
            await update.message.reply_text("دریافت قیمت نقره ممکن نیست.")
    else:
        await update.message.reply_text("فقط بنویس: طلا یا نقره.")

# ==================== Daily Price Endpoint ====================


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

# ==================== Run ====================


if __name__ == '__main__':
    keep_alive()

    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, metal_handler))
    app.run_polling()
