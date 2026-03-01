from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

TOKEN = "8623819950:AAH1mw7tyZbr_uEnrofFilXLyGV7XK1P_8w"

# --- Підключення до Google Sheets ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)

sheet = client.open("IQOS_Grafik").sheet1  # Назва таблиці

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Тімченко Аліна", "Котова Олександра"],
                ["Марініна Ірина", "Рибіна Катерина"],
                ["Кех Евеліна"]]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Оберіть своє ім'я:", reply_markup=reply_markup)

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