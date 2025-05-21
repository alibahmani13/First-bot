import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging
logging.basicConfig(format='%(name)s - %(asctime)s - %(levelname)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
API_TOKEN = "7429159046:AAHpSDjy2lv2b-vaAqneLrkCCnvk3qmKImU"
GOLDAPI_KEY = "goldapi-3v4m1smawx0q3m-io"

# تابع گرفتن قیمت از goldapi


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

# هندلر دستور /start


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! قیمت چی رو می‌خوای؟\nبنویس: طلا یا نقره")

# هندلر پیام‌های متنی برای طلا و نقره


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

# شروع ربات و ثبت هندلرها
if __name__ == '__main__':
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(
        filters.TEXT & (~filters.COMMAND), metal_handler))

    app.run_polling()
