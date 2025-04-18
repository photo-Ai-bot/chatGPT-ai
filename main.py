import openai
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# توکن ربات تلگرام خود را اینجا وارد کنید
BOT_TOKEN = "BOT_TOKEN"

# تنظیمات OpenAI
openai.api_key = "API_KEY_OPENAI"

# پرامپت‌ها
PROMPT_1 = "این عکس را طوری ویرایش کن که انگار با یک دوربین حرفه‌ای گرفته شده. نورپردازی باید ملایم و سینمایی باشه، با کنتراست مناسب و رنگ‌های طبیعی اما گرم. کمی فضا رو تیره کن تا حالت دراماتیک و جذاب‌تری بگیره. جزئیات صورت واضح، پوست صاف و تمیز، پس‌زمینه کمی تار و با عمق میدان بالا. انگار عکس در یک محیط شهری مدرن یا کافی‌شاپ لوکس شب‌هنگام یا.... گرفته شده. حس حرفه‌ای بودن، وضوح بالا و ترکیب رنگی جذاب باید توی عکس حس بشه."
PROMPT_2 = "تصویر دریافتی را به گونه‌ای ویرایش کن که انگار با یک دوربین فوق‌پیشرفته در آینده گرفته شده است. کیفیت تصویر را بالا ببر، نورپردازی دقیق و واقعی انجام بده، اما تم تصویر را کمی سرد و تیره نگه دار. از المان‌هایی استفاده کن که حس یک دنیای آینده‌نگر، هوشمند و رباتیک را القا کنند؛ مانند نورهای نئونی، سازه‌های متالیک، سطوح دیجیتالی یا هولوگرام‌ها. تمامی جزئیات تصویر باید واقعی و دقیق باشند تا تصویر نهایی کاملاً حرفه‌ای و آینده‌محور به نظر برسد."

# حالت‌های مکالمه
SELECT_MODEL = 1

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً یک عکس بفرست که ویرایش کنم.")

# دریافت عکس
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ذخیره عکس
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_path = f"temp_{update.message.from_user.id}.jpg"
    await file.download_to_drive(file_path)

    # ذخیره عکس در داده‌های کاربر
    context.user_data["photo_path"] = file_path
    await update.message.reply_text("کدوم مدل رو انتخاب می‌کنی؟\n1️⃣ ادیت مدرن\n2️⃣ ادیت آینده")
    return SELECT_MODEL

# انتخاب مدل و ارسال به OpenAI برای ویرایش
async def select_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    model = update.message.text.strip()
    photo_path = context.user_data.get("photo_path")
    
    if not photo_path:
        await update.message.reply_text("مشکلی پیش اومد. لطفاً دوباره عکس بفرست.")
        return ConversationHandler.END

    # انتخاب پرامپت بر اساس مدل
    if model == "1":
        prompt = PROMPT_1
    elif model == "2":
        prompt = PROMPT_2
    else:
        await update.message.reply_text("فقط 1 یا 2 لطفاً انتخاب کن.")
        return SELECT_MODEL

    await update.message.reply_text("در حال ویرایش عکس... لطفاً چند لحظه صبر کن.")

    # ارسال عکس به OpenAI برای ویرایش
    with open(photo_path, "rb") as img_file:
        response = openai.Image.create_edit(
            image=img_file,
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

    image_url = response['data'][0]['url']

    # ارسال عکس ویرایش‌شده به کاربر
    await update.message.reply_photo(photo=image_url)

    # حذف عکس موقت
    os.remove(photo_path)
    return ConversationHandler.END

# لغو عملیات
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لغو شد.")
    return ConversationHandler.END

# تنظیمات اصلی ربات
app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.PHOTO, handle_photo)],
    states={SELECT_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_model)]},
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)

app.run_polling()
