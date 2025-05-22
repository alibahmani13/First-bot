import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, Response
from threading import Thread
import logging
import os

logging.basicConfig(format='%(name)s - %(asctime)s - %(levelname)s ',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = "7429159046:AAGYuqgAt0VE9vf9rPmuM-Hwpq-Qwut0z0g"
GOLDAPI_KEY = "goldapi-3v4m1smawx0q3m-io"


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


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! قیمت چی رو می‌خوای؟\nبنویس: طلا یا نقره")


async def metal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if text == "طلا":
        price = get_price("XAU")
        if price:
            await update.message.reply_text(f"قیمت طلا: {price} دلار")
        else:
            await update.message.reply_text("خطا در دریافت قیمت طلا.")
    elif text == "نقره":
        price = get_price("XAG")
        if price:
            await update.message.reply_text(f"قیمت نقره: {price} دلار")
        else:
            await update.message.reply_text("خطا در دریافت قیمت نقره.")
    else:
        await update.message.reply_text("لطفاً فقط بنویس: طلا یا نقره.")


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


if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), metal_handler))
    app.run_polling()
    print("Bot is working")
