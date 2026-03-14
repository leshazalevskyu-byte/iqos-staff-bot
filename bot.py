from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import gspread
from google.oauth2.service_account import Credentials

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import os
import json


TOKEN = os.environ["BOT_TOKEN"]

# ---------- Google Sheets ----------

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

client = gspread.authorize(creds)

sheet = client.open("IQOS_Grafik").sheet1


# ---------- українські місяці ----------

months = {
    1: "січня",
    2: "лютого",
    3: "березня",
    4: "квітня",
    5: "травня",
    6: "червня",
    7: "липня",
    8: "серпня",
    9: "вересня",
    10: "жовтня",
    11: "листопада",
    12: "грудня"
}


# ---------- головне меню ----------

def main_menu():

    keyboard = [
        ["👥 Хто сьогодні працює"],
        ["📋 Всі задачі на сьогодні"],
        ["📅 Хто завтра працює"]
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ---------- /start ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    now = datetime.now(ZoneInfo("Europe/Kyiv"))

    today_pretty = f"{now.day} {months[now.month]}"

    await update.message.reply_text(
        f"📅 Сьогодні {today_pretty}\n\nОберіть дію:",
        reply_markup=main_menu()
    )


# ---------- обробка кнопок ----------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    selected = update.message.text

    now = datetime.now(ZoneInfo("Europe/Kyiv"))

    today = now.strftime("%Y-%m-%d")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    today_pretty = f"{now.day} {months[now.month]}"

    records = sheet.get_all_records()


    # ---------- назад ----------

    if selected == "⬅️ Назад":

        await update.message.reply_text(
            f"📅 Сьогодні {today_pretty}\n\nОберіть дію:",
            reply_markup=main_menu()
        )
        return


    # ---------- хто сьогодні працює ----------

    if selected == "👥 Хто сьогодні працює":

        employees = []

        for row in records:
            if today in str(row["Date"]):
                employees.append(row["Name"])

        employees = list(set(employees))

        if not employees:

            await update.message.reply_text("❌ Сьогодні ніхто не працює")
            return

        keyboard = [[e] for e in employees]

        keyboard.append(["⬅️ Назад"])

        await update.message.reply_text(
            "👥 Оберіть працівника:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

        return


    # ---------- задачі конкретного працівника ----------

    employee_tasks = []

    for row in records:

        if selected == row["Name"] and today in str(row["Date"]):

            employee_tasks.append(row["Task"])

    if employee_tasks:

        text = f"📋 Задачі для {selected}:\n\n"

        for task in employee_tasks:
            text += f"• {task}\n"

        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup([["⬅️ Назад"]], resize_keyboard=True)
        )

        return


    # ---------- всі задачі ----------

    if selected == "📋 Всі задачі на сьогодні":

        tasks = []

        for row in records:

            if today in str(row["Date"]):

                tasks.append(f"{row['Name']} — {row['Task']}")

        if not tasks:

            text = "❌ На сьогодні задач немає"

        else:

            text = "📋 Задачі на сьогодні:\n\n" + "\n".join(tasks)

        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup([["⬅️ Назад"]], resize_keyboard=True)
        )

        return


    # ---------- хто завтра працює ----------

    if selected == "📅 Хто завтра працює":

        employees = []
        for row in records:

            if tomorrow in str(row["Date"]):

                employees.append(row["Name"])

        employees = list(set(employees))

        if not employees:

            text = "❌ Завтра ніхто не працює"

        else:

            text = "📅 Завтра працюють:\n\n"

            for e in employees:

                text += f"• {e}\n"

        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup([["⬅️ Назад"]], resize_keyboard=True)
        )

        return


# ---------- запуск ----------

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()
