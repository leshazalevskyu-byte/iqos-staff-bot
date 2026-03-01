from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

import os
TOKEN = os.environ["BOT_TOKEN"]

# --- Підключення до Google Sheets ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

import json

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

sheet = client.open("IQOS_Grafik").sheet1  # Назва таблиці

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y-%m-%d")
    records = sheet.get_all_records()

    today_employees = []

    for row in records:
        if str(row["Date"]) == today:
            today_employees.append(row["Name"])

    today_employees = list(set(today_employees))

    if not today_employees:
        await update.message.reply_text("❌ Сьогодні ніхто не працює.")
        return

    keyboard = [[name] for name in today_employees]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"📅 Сьогодні {today}\n\nОберіть працівника:",
        reply_markup=reply_markup
    )

# --- Обробка вибору ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M")

    sheet.append_row([date, name, time])

    await update.message.reply_text(f"✅ {name}, запис збережено!")

# --- Запуск ---
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Бот запущений...")

app.run_polling()

