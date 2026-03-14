import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ---------------- GOOGLE SHEETS ----------------

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open("IQOS_Grafik").sheet1

# ---------------- МІСЯЦІ ----------------

months = {
1:"січня",2:"лютого",3:"березня",4:"квітня",
5:"травня",6:"червня",7:"липня",8:"серпня",
9:"вересня",10:"жовтня",11:"листопада",12:"грудня"
}

# ---------------- МЕНЮ ----------------

def main_menu():

    keyboard = [
        ["👥 Хто сьогодні працює"],
        ["📋 Всі задачі на сьогодні"],
        ["📅 Хто завтра працює"]
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ---------------- START ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    now = datetime.now(ZoneInfo("Europe/Kyiv"))

    today_pretty = f"{now.day} {months[now.month]}"

    await update.message.reply_text(
        f"📅 Сьогодні {today_pretty}\n\nОберіть дію:",
        reply_markup=main_menu()
    )

# ---------------- ОБРОБКА ----------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    now = datetime.now(ZoneInfo("Europe/Kyiv"))

    today = now.strftime("%Y-%m-%d")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    records = sheet.get_all_records()

# ---------------- ХТО СЬОГОДНІ ----------------

    if text == "👥 Хто сьогодні працює":

        employees = []

        for row in records:

            if str(row["Date"]) == today:

                employees.append(row["Name"])

        employees = list(set(employees))

        keyboard = [[name] for name in employees]

        keyboard.append(["⬅️ Назад"])

        await update.message.reply_text(
            "👥 Оберіть працівника:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

        return

# ---------------- ХТО ЗАВТРА ----------------

    if text == "📅 Хто завтра працює":

        employees = []

        for row in records:

            if str(row["Date"]) == tomorrow:

                employees.append(row["Name"])

        employees = list(set(employees))

        if not employees:

            await update.message.reply_text("❌ Ніхто не працює")

            return

        message = "📅 Завтра працюють:\n\n"

        for e in employees:

            message += f"• {e}\n"

        await update.message.reply_text(message)

        return

# ---------------- ВСІ ЗАДАЧІ ----------------

    if text == "📋 Всі задачі на сьогодні":

        tasks = []

        for row in records:

            if str(row["Date"]) == today:

                name = row["Name"]

                task_list = str(row["Tasks"]).split(";")

                for t in task_list:

                    tasks.append(f"{name} — {t.strip()}")

        if not tasks:

            await update.message.reply_text("❌ Немає задач")

            return

        message = "📋 Задачі на сьогодні:\n\n"

        for t in tasks:

            message += f"• {t}\n"

        await update.message.reply_text(message)

        return

# ---------------- НАЗАД ----------------

    if text == "⬅️ Назад":

        await start(update, context)

        return

# ---------------- ЗАДАЧІ ПРАЦІВНИКА ----------------

    employee_tasks = []

    for row in records:

        if str(row["Date"]) == today and row["Name"] == text:

            tasks = str(row["Tasks"]).split(";")

            for t in tasks:

                employee_tasks.append(t.strip())

    if employee_tasks:

        message = f"📋 Задачі для {text}\n\n"

        for t in employee_tasks:
            message += f"• {t}\n"

        await update.message.reply_text(message)

        return

# ---------------- ЗАПУСК ----------------

def main():

    token = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
