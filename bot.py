from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import os
import json

TOKEN = os.environ["BOT_TOKEN"]

# --- Підключення до Google Sheets ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

sheet = client.open("IQOS_Grafik").sheet1


# --- Головне меню ---
def main_menu():
    keyboard = [
        ["👥 Хто сьогодні працює"],
        ["📋 Всі задачі на сьогодні"],
        ["📅 Хто завтра працює"]
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    today = datetime.now().strftime("%Y-%m-%d")

    await update.message.reply_text(
        f"📅 Сьогодні {today}\n\nОберіть дію:",
        reply_markup=main_menu()
    )


# --- Обробка кнопок ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    selected_name = update.message.text

    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    records = sheet.get_all_records()

    # ⬅️ Назад
    if selected_name == "⬅️ Назад":

        await update.message.reply_text(
            f"📅 Сьогодні {today}\n\nОберіть дію:",
            reply_markup=main_menu()
        )
        return


    # 👥 Хто сьогодні працює
    if selected_name == "👥 Хто сьогодні працює":

        employees = []

        for row in records:
            if str(row["Date"])[:10] == today:
                employees.append(row["Name"])

        employees = list(set(employees))

        if not employees:
            await update.message.reply_text("❌ Сьогодні ніхто не працює.")
            return

        text = "👥 Сьогодні працюють:\n\n"

        for e in employees:
            text += f"• {e}\n"

        keyboard = [["⬅️ Назад"]]

        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return


    # 📅 Хто завтра працює
    if selected_name == "📅 Хто завтра працює":

        employees = []

        for row in records:
            if str(row["Date"])[:10] == tomorrow:
                employees.append(row["Name"])

        employees = list(set(employees))

        if not employees:
            await update.message.reply_text("❌ Завтра ще немає змін.")
            return

        text = "📅 Завтра працюють:\n\n"

        for e in employees:
            text += f"• {e}\n"

        keyboard = [["⬅️ Назад"]]

        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return


    # 📋 Всі задачі на сьогодні
    if selected_name == "📋 Всі задачі на сьогодні":

        text = "📋 Задачі на сьогодні:\n\n"

        for row in records:
            if str(row["Date"])[:10] == today:
                text += f"👤 {row['Name']}\n"
                text += f"{row['Task']}\n\n"

        keyboard = [["⬅️ Назад"]]

        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return


# --- Запуск бота ---
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

app.run_polling()
