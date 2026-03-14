from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import gspread
from google.oauth2.service_account import Credentials

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import os
import json


TOKEN = os.environ["BOT_TOKEN"]

# --- Google Sheets підключення ---

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

client = gspread.authorize(creds)

sheet = client.open("IQOS_Grafik").sheet1


# --- Меню ---

def main_menu():
    keyboard = [
        ["👥 Хто сьогодні працює"],
        ["📋 Всі задачі на сьогодні"],
        ["📅 Хто завтра працює"]
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# --- /start ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    today = datetime.now(ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%d")

    await update.message.reply_text(
        f"📅 Сьогодні {today}\n\nОберіть дію:",
        reply_markup=main_menu()
    )


# --- обробка кнопок ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    selected_name = update.message.text

    today = datetime.now(ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%d")
    tomorrow = (datetime.now(ZoneInfo("Europe/Kyiv")) + timedelta(days=1)).strftime("%Y-%m-%d")

    records = sheet.get_all_records()


    # --- назад у меню ---

    if selected_name == "⬅️ Назад":

        await update.message.reply_text(
            f"📅 Сьогодні {today}\n\nОберіть дію:",
            reply_markup=main_menu()
        )
        return


    # --- хто сьогодні працює ---

    if selected_name == "👥 Хто сьогодні працює":

        employees = []

        for row in records:
            if today in str(row["Date"]):
                employees.append(row["Name"])

        employees = list(set(employees))

        if not employees:
            text = "❌ Сьогодні ніхто не працює."
        else:
            text = "👥 Сьогодні працюють:\n\n" + "\n".join([f"• {e}" for e in employees])

        keyboard = [["⬅️ Назад"]]

        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

        return


    # --- хто завтра працює ---

    if selected_name == "📅 Хто завтра працює":

        employees = []

        for row in records:
            if tomorrow in str(row["Date"]):
                employees.append(row["Name"])

        employees = list(set(employees))

        if not employees:
            text = "❌ Завтра ніхто не працює."
        else:
            text = "📅 Завтра працюють:\n\n" + "\n".join([f"• {e}" for e in employees])

        keyboard = [["⬅️ Назад"]]

        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

        return


    # --- всі задачі на сьогодні ---

    if selected_name == "📋 Всі задачі на сьогодні":

        tasks = []

        for row in records:
            if today in str(row["Date"]):
                tasks.append(f"{row['Name']} — {row['Task']}")

        if not tasks:
            text = "❌ На сьогодні задач немає."
        else:
            text = "📋 Задачі на сьогодні:\n\n" + "\n".join(tasks)

        keyboard = [["⬅️ Назад"]]

        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

        return


# --- запуск бота ---

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()
