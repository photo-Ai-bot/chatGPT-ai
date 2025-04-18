from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import openai
import requests
from io import BytesIO

BOT_TOKEN = os.environ["BOT_TOKEN"]
openai.api_key = os.environ["OPENAI_API_KEY"]

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً یه عکس برام بفرست.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عکس دریافت شد، لطفاً چند لحظه صبر کن...")

    # دریافت عکس از تلگرام
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_url = file.file_path
    response = requests.get(file_url)
    img_data = BytesIO(response.content)

    try:
        await update.message.reply_text("فعلاً فقط تصویر رو دریافت می‌کنم، نسخه واقعی در مرحله بعد پیاده‌سازی می‌شه.")
        
        img_data.seek(0)
        await update.message.reply_photo(photo=InputFile(img_data, filename="edited.jpg"))

    except Exception as e:
        await update.message.reply_text(f"یه مشکلی پیش اومد: {e}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

app.run_polling()
