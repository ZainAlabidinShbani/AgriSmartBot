import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler

from advice import crops, crop_advices, get_random_tip
from weather import fetch_weather_by_coords, fetch_forecast_by_coords

# ======================
# إعداد متغيرات البيئة
# ======================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN غير محدد!")

# ======================
# إعدادات البوت
# ======================
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
subscribers = set()  # يمكن لاحقاً حفظها في ملف JSON

# ======================
# القوائم (UI)
# ======================
def get_main_menu():
    keyboard = [
        [KeyboardButton("🤖 الاستعانة بالذكاء الاصطناعي"), KeyboardButton("🌾 المحاصيل")],
        [KeyboardButton("📅 توقعات 3 أيام"), KeyboardButton("🌦 الطقس الحالي")],
        [KeyboardButton("🗺 الخرائط الزراعية")],
        [KeyboardButton("/subscribe"), KeyboardButton("/unsubscribe")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_crops_menu():
    rows = []
    for i in range(0, len(crops), 2):
        row = crops[i:i+2]
        rows.append([KeyboardButton(c) for c in row])
    rows.append([KeyboardButton("⬅️ رجوع للقائمة")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def get_weather_menu(back_text="⬅️ رجوع للقائمة"):
    keyboard = [
        [KeyboardButton("📍 أرسل موقعي", request_location=True)],
        [KeyboardButton(back_text)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ======================
# أوامر البوت
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👨‍🌾 أهلاً بك! اختر من القائمة:", reply_markup=get_main_menu())

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers.add(chat_id)
    await update.message.reply_text("✅ تم الاشتراك في التنبيهات اليومية.")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers.discard(chat_id)
    await update.message.reply_text("❌ تم إلغاء الاشتراك من التنبيهات.")

# ======================
# التعامل مع الرسائل
# ======================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["last_choice"] = text

    if text == "🌾 المحاصيل":
        await update.message.reply_text("📋 اختر المحصول:", reply_markup=get_crops_menu())

    elif text in crops:
        info = crop_advices.get(text, {})
        if info:
            # إرسال كل قسم في رسالة منفصلة
            await update.message.reply_text(f"📌 نصائح موسعة لـ {text}:", reply_markup=get_crops_menu())
            await update.message.reply_text(f"🌱 طرق الزراعة:\n{info['طرق_الزراعة']}")
            await update.message.reply_text(f"🗓 المواعيد الموسمية:\n{info['المواعيد']}")
            steps_text = "📝 خطوات عملية متسلسلة:\n"
            for i, step in enumerate(info["خطوات"], 1):
                steps_text += f"{i}. {step}\n"
            await update.message.reply_text(steps_text)
            await update.message.reply_text(f"⚠️ تحذيرات مهمة:\n{info['تحذيرات']}")
        else:
            await update.message.reply_text("❌ لا توجد معلومات متاحة لهذا المحصول.", reply_markup=get_crops_menu())

    elif text == "🤖 الاستعانة بالذكاء الاصطناعي":
        await update.message.reply_text("🚧 ميزة الذكاء الاصطناعي غير مفعلة حالياً.", reply_markup=get_main_menu())

    elif text == "🌦 الطقس الحالي":
        await update.message.reply_text("📍 أرسل موقعك للحصول على الطقس الحالي:", reply_markup=get_weather_menu())

    elif text == "📅 توقعات 3 أيام":
        await update.message.reply_text("📍 أرسل موقعك للحصول على توقعات الطقس لـ 3 أيام:", reply_markup=get_weather_menu())

    elif text == "🗺 الخرائط الزراعية":
        await update.message.reply_text("🗺 ميزة الخرائط الزراعية قيد التطوير 🚧", reply_markup=get_main_menu())

    elif text == "⬅️ رجوع للقائمة":
        await update.message.reply_text("⬅️ رجعت للقائمة الرئيسية.\nاختر من جديد:", reply_markup=get_main_menu())

    else:
        await update.message.reply_text("❌ لم أفهم رسالتك، اختر من القائمة.", reply_markup=get_main_menu())

# ======================
# التعامل مع الموقع
# ======================
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    if not loc:
        return
    last_choice = context.user_data.get("last_choice", "")
    if last_choice == "📅 توقعات 3 أيام":
        forecast = fetch_forecast_by_coords(loc.latitude, loc.longitude)
        await update.message.reply_text(forecast, reply_markup=get_main_menu())
    else:
        weather = fetch_weather_by_coords(loc.latitude, loc.longitude)
        await update.message.reply_text(weather, reply_markup=get_main_menu())

# ======================
# التنبيهات اليومية
# ======================
async def daily_job(app: Application):
    for chat_id in subscribers:
        msg = get_random_tip()
        try:
            await app.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            logging.error(f"خطأ عند الإرسال إلى {chat_id}: {e}")

def start_scheduler(app: Application):
    scheduler = BackgroundScheduler(timezone="Asia/Damascus")
    scheduler.add_job(lambda: asyncio.create_task(daily_job(app)), trigger="cron", hour=8, minute=0)
    scheduler.start()

# ======================
# تشغيل البوت
# ======================
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # أوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # رسائل ونصوص
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # بدء جدولة التنبيهات اليومية
    start_scheduler(app)

    print("✅ البوت يعمل — استعد لاستقبال الرسائل.")
    app.run_polling()

if __name__ == "__main__":
    main()
