from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

import os
import re
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

sheet = client.open("IQOS_Grafik").sheet1


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

# --- Обробка вибору ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

selected_name = update.message.text
today = datetime.now().strftime("%Y-%m-%d")
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
records = sheet.get_all_records()

# ⬅️ Назад у головне меню
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

    text = "👥 Сьогодні працюють:\n\n"

    for e in employees:
        text += f"• {e}\n"

    keyboard = [[name] for name in employees]
    keyboard.append(["⬅️ Назад"])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(text, reply_markup=reply_markup)
    return

# 📅 Хто завтра працює
if selected_name == "📅 Хто завтра працює":

    employees = []

    for row in records:
        if str(row["Date"])[:10] == tomorrow:
            employees.append(row["Name"])

    employees = list(set(employees))

    if not employees:
       await update.message.reply_text("📅 На завтра ще немає змін")
       return

    text = "📅 Завтра працюють:\n\n"

    for e in employees:
        text += f"• {e}\n"

    keyboard = [["⬅️ Назад"]]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(text, reply_markup=reply_markup)
    return

# 📋 Всі задачі на сьогодні
if selected_name == "📋 Всі задачі на сьогодні":

    text = "📋 Завдання на сьогодні:\n\n"

    for row in records:
        if str(row["Date"])[:10] == today:

            name = row["Name"]
            tasks = row["Tasks"]

            text += f"👤 {name}\n"

            for task in tasks.split(";"):
                text += f"• {task.strip()}\n"

            text += "\n"

    await update.message.reply_text(text)
    return


# 👤 Завдання конкретного працівника
for row in records:

    if str(row["Date"])[:10] == today and row["Name"] == selected_name:

        shift = row["Shift"]
        tasks = row["Tasks"]

        text = f"👤 {selected_name}\n\n"
        text += f"🕒 Зміна: {shift}\n\n"
        text += "📋 Завдання:\n"

        for task in tasks.split(";"):
            text += f"• {task.strip()}\n"

        keyboard = [["⬅️ Назад"]]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(text, reply_markup=reply_markup)
        return

for row in records:
    if str(row["Date"]).strip()[:10] == today and row["Name"].strip() == selected_name.strip():
        shift = row["Shift"]
        tasks = row["Tasks"]
        tasks_list = re.split(r"[;；]", tasks)
        formatted_tasks = "\n".join([f"• {task.strip()}" for task in tasks_list])

        await update.message.reply_text(
            f"👤 {selected_name}\n"
            f"🕒 Зміна: {shift}\n\n"
            f"📋 Обов’язки:\n{formatted_tasks}"
        )
        return

await update.message.reply_text("❌ Дані не знайдено.")

# --- Запуск ---
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Бот запущений...")

app.run_polling()







