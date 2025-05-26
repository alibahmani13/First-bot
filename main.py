import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, Response
from threading import Thread
import logging
import os
import time
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
MY_CHAT_ID = os.getenv("MY_CHAT_ID")
API_KEY = os.getenv("API_KEY")

logging.basicConfig(level=logging.INFO)

# ======== Flask setup to keep bot alive ========

flask_app = Flask('')


@flask_app.route('/')
def home():
    return "🤖 ربات فعال است!"


@flask_app.route('/', methods=['HEAD'])
def head():
    return Response(status=200)


def run():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()


# ======== Get market prices from API ========

def get_market_prices():
    url = f"https://BrsApi.ir/Api/Market/Gold_Currency.php?key={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"API Status Code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error in get_market_prices: {e}")
    return None


# ======== Inline Keyboards ========

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("💎 طلا", callback_data='gold')],
        [InlineKeyboardButton("💵 ارز", callback_data='currency')],
        [InlineKeyboardButton("🪙 رمزارز", callback_data='crypto')],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_keyboard():
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data='back')]]
    return InlineKeyboardMarkup(keyboard)


# ======== Helper Icons ========

# ایموجی برای طلا
GOLD_ICONS = {
    "مثقال طلا": "⚖️",
    "اونس طلا": "🪙",
    "طلای 18 عیار": "🟡",
    "طلای 24 عیار": "🟠",
    "گرم طلا": "🔶",
    "سکه امامی": "🥇",
    "نیم سکه": "🥈",
    "ربع سکه": "🥉",
    "سکه گرمی": "🪙",
}

# ایموجی برای رمزارزها
CRYPTO_ICONS = {
    "بیت‌کوین": "₿",
    "اتریوم": "♦️",
    "تتر": "🟢",
    "ایکس‌آر‌پی": "✕",
    "بی‌ان‌بی": "🅱️",
    "سولانا": "🚣",
    "یواس‌دی کوین": "💵",
    "دوج‌کوین": "🐕",
    "کاردانو": "🅰️",
    "ترون": "⚜️",
    "چین‌لینک": "🔗",
    "آوالانچ": "🏔️",
    "استلار": "⭐",
    "شیبا اینو": "🐕",
    "لایت‌کوین": "🪽",
    "پولکادات": "●",
    "یونی‌سواپ": "🦄",
    "کازماس": "🪐",
    "فایل‌کوین": "📁"
}

CRYPTO_SYMBOLS = {
    "بیت‌کوین": "BTC",
    "اتریوم": "ETH",
    "تتر": "USDT",
    "ایکس‌آر‌پی": "XRP",
    "بی‌ان‌بی": "BNB",
    "سولانا": "SOL",
    "یواس‌دی کوین": "USDC",
    "دوج‌کوین": "DOGE",
    "کاردانو": "ADA",
    "ترون": "TRX",
    "چین‌لینک": "LINK",
    "آوالانچ": "AVAX",
    "استلار": "XLM",
    "شیبا اینو": "SHIB",
    "لایت‌کوین": "LTC",
    "پولکادات": "DOT",
    "یونی‌سواپ": "UNI",
    "کازماس": "ATOM",
    "فایل‌کوین": "FIL"
}


def format_crypto_change(change_str):
    try:
        change_float = float(
            str(change_str).replace('%', '').replace(',', '.'))
        if change_float > 0:
            return f"🔺 🟢 {change_float}%"
        elif change_float < 0:
            return f"🔻 🔴 {abs(change_float)}%"
        else:
            return f"⏺ ⚪ 0%"
    except:
        return f"⏺ ⚪ {change_str}"


# ======== Handlers ========

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام! لطفاً دسته‌بندی مورد نظر خود را انتخاب کنید:",
        reply_markup=main_menu_keyboard()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = get_market_prices()
    if not data:
        await query.edit_message_text(
            "⚠️ خطا در دریافت اطلاعات بازار. لطفاً دوباره تلاش کنید.",
            reply_markup=back_keyboard()
        )
        return

    if query.data == 'gold':
        msg = "💎 قیمت‌های طلا:\n" + ("─" * 30) + "\n"
        for item in data.get('gold', []):
            name = item.get('name', 'نامشخص')
            price = item.get('price', 'نامشخص')
            unit = item.get('unit', '')
            icon = GOLD_ICONS.get(name, "🔸")
            msg += f"• {icon} {name}: {price} {unit}\n"

        await query.edit_message_text(msg, reply_markup=back_keyboard())

    elif query.data == 'currency':
        msg = "💵 قیمت‌های ارز:\n" + ("─" * 30) + "\n"
        for item in data.get('currency', []):
            name = item.get('name', 'نامشخص')
            price = item.get('price', 'نامشخص')
            unit = item.get('unit', '')
            flag = CURRENCY_FLAGS.get(name, "")
            msg += f"• {flag} {name}: {price} {unit}\n"

        await query.edit_message_text(msg, reply_markup=back_keyboard())

    elif query.data == 'crypto':
        msg = "🪙 قیمت‌های رمزارز:\n" + ("─" * 30) + "\n"
        for item in data.get('cryptocurrency', []):
            name = item.get('name', 'نامشخص')
            price = item.get('price', 'نامشخص')
            unit = item.get('unit', '')
            change = item.get('change_percent', 'نامشخص')

            icon = CRYPTO_ICONS.get(name, "🪙")
            change_formatted = format_crypto_change(change)

            msg += f"• {icon} {name}: {price} {unit} (تغییر: {change_formatted})\n"

        await query.edit_message_text(msg, reply_markup=back_keyboard())

    elif query.data == 'back':
        await query.edit_message_text(
            "👈 دسته‌بندی مورد نظر خود را انتخاب کنید:",
            reply_markup=main_menu_keyboard()
        )


# ======== Currency flags map (used in multiple places) ========

CURRENCY_FLAGS = {
    "دلار": "🇺🇸",
    "یورو": "🇪🇺",
    "درهم امارات": "🇦🇪",
    "پوند": "🇬🇧",
    "ین ژاپن": "🇯🇵",
    "دینار کویت": "🇰🇼",
    "دلار استرالیا": "🇦🇺",
    "دلار کانادا": "🇨🇦",
    "یوآن چین": "🇨🇳",
    "لیر ترکیه": "🇹🇷",
    "ریال عربستان": "🇸🇦",
    "فرانک سوئیس": "🇨🇭",
    "روپیه هند": "🇮🇳",
    "روپیه پاکستان": "🇵🇰",
    "دینار عراق": "🇮🇶",
    "لیر سوریه": "🇸🇾",
    "کرون سوئد": "🇸🇪",
    "ریال قطر": "🇶🇦",
    "ریال عمان": "🇴🇲",
    "دینار بحرین": "🇧🇭",
    "افغانی": "🇦🇫",
    "رینگیت مالزی": "🇲🇾",
    "بات تایلند": "🇹🇭",
    "روبل روسیه": "🇷🇺",
    "منات آذربایجان": "🇦🇿",
    "درام ارمنستان": "🇦🇲",
    "لاری گرجستان": "🇬🇪",
}


# ======== Auto send prices every 24h ========

def auto_send_prices():
    while True:
        data = get_market_prices()
        if data:
            message = "⏰ قیمت‌های خودکار (هر 24 ساعت):\n\n"

            message += "💎 طلا:\n" + ("─" * 25) + "\n"
            for item in data.get('gold', []):
                name = item.get('name', 'نامشخص')
                price = item.get('price', 'نامشخص')
                unit = item.get('unit', '')
                icon = GOLD_ICONS.get(name, "🔸")
                message += f"• {icon} {name}: {price} {unit}\n"

            message += "\n💵 ارز:\n" + ("─" * 25) + "\n"
            for item in data.get('currency', []):
                name = item.get('name', 'نامشخص')
                price = item.get('price', 'نامشخص')
                unit = item.get('unit', '')
                flag = CURRENCY_FLAGS.get(name, "")
                message += f"• {flag} {name}: {price} {unit}\n"

            message += "\n🪙 رمزارز:\n" + ("─" * 25) + "\n"
            for item in data.get('cryptocurrency', []):
                name = item.get('name', 'نامشخص')
                price = item.get('price', 'نامشخص')
                unit = item.get('unit', '')
                change_percent = item.get('change_percent', 'نامشخص')

                icon = CRYPTO_ICONS.get(name, "🪙")
                change_formatted = format_crypto_change(change_percent)

                message += f"• {icon} {name}: {price} {unit} (تغییر: {change_formatted})\n"

        else:
            message = "⚠️ خطا در دریافت قیمت خودکار."

        try:
            requests.get(
                f"https://api.telegram.org/bot{API_TOKEN}/sendMessage",
                params={
                    "chat_id": MY_CHAT_ID,
                    "text": message
                }
            )
        except Exception as e:
            logging.error(f"Error sending auto message: {e}")

        time.sleep(86400)  # هر 24 ساعت


# ======== Run bot ========

if __name__ == '__main__':
    keep_alive()
    Thread(target=auto_send_prices, daemon=True).start()

    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()
