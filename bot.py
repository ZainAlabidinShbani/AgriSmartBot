import os
import logging
import random
import requests
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

# ======================
# تحميل متغيرات البيئة
# ======================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN غير محدد!")
if not OPENWEATHER_API_KEY:
    raise RuntimeError("❌ OPENWEATHER_API_KEY غير محدد!")

# ======================
# إعدادات البوت
# ======================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

DEFAULT_CITY = "Latakia"  # المدينة الافتراضية للطقس

# قائمة النصائح الزراعية العشوائية
random_tips = [
    "قم بري النباتات في الصباح الباكر لتقليل التبخر.",
    "تجنب الري في ساعات الظهيرة الحارة.",
    "استخدم السماد العضوي لتحسين جودة التربة.",
    "راقب النباتات بانتظام لاكتشاف أي آفات مبكراً.",
    "التقليم المنتظم يساعد على زيادة الإنتاج."
]

# المستخدمين المشتركين
subscribers = set()

# قائمة المحاصيل السورية
crops = ["قمح", "زيتون", "قطن", "عنب", "حمضيات"]

# قاعدة بيانات نصائح لكل محصول
crop_advices = {
    "قمح": [
        "💧 الري: يفضل الري كل 15-20 يوم بالربيع، وتقليل الري عند امتلاء السنابل.",
        "🌱 التسميد: إضافة اليوريا بعد الإنبات ثم الفوسفور قبل التفريع.",
        "🐛 مكافحة: مراقبة حشرة السونة ورش المبيدات عند الحاجة.",
        "🌾 الحصاد: احصد عندما تميل السنابل للون الذهبي ويجف العود.",
        "🏠 التخزين: خزن القمح بمكان جاف بعيد عن الرطوبة."
    ],
    "زيتون": [
        "💧 الري: ري تكميلي بالصيف كل 3-4 أسابيع خاصة في سنوات الجفاف.",
        "🌱 التسميد: إضافة السماد العضوي شتاءً والآزوت على دفعات ربيعية.",
        "🐛 مكافحة: متابعة ذبابة الزيتون ورش الطعوم البروتينية.",
        "🌳 الخدمة: تقليم خفيف بعد القطاف لزيادة التهوية.",
        "🏠 التخزين: يفضل عصر الثمار مباشرة لتفادي التزنخ."
    ],
    "قطن": [
        "💧 الري: يحتاج ري غزير كل 10-12 يوم خصوصاً بفترة التزهير.",
        "🌱 التسميد: التوازن بين الآزوت والبوتاسيوم مهم لزيادة الألياف.",
        "🐛 مكافحة: مكافحة دودة اللوز بأصناف مبيدات متناوبة.",
        "🌾 الحصاد: اجمع القطن بعد تفتح الجوزات بـ 60-70%.",
        "🏠 التخزين: احرص على أن تكون الأكياس جافة ونظيفة."
    ],
    "عنب": [
        "💧 الري: قلل الري وقت التزهير لزيادة العقد، وزد عند امتلاء الحبات.",
        "🌱 التسميد: التسميد العضوي شتاءً، والآزوت قبل التزهير.",
        "🐛 مكافحة: البياض الدقيقي والبياض الزغبي أخطر الآفات — الرش بالكبريت أو النحاس ضروري.",
        "🌿 الخدمة: تقليم شتوي جيد لزيادة التهوية وتقليل الأمراض.",
        "🍇 الحصاد: يقطف العنب عندما يكتمل السكر ويصبح الطعم حلو."
    ],
    "حمضيات": [
        "💧 الري: تجنب الغمر، واستعمل الري بالتنقيط لتفادي تعفن الجذور.",
        "🌱 التسميد: إضافة الآزوت دفعات ربيعية وبوتاسيوم مع العقد.",
        "🐛 مكافحة: الحذر من المن والحشرة القشرية — استخدام الزيوت المعدنية.",
        "🌳 الخدمة: تقليم خفيف لفتح قلب الشجرة ودخول الشمس.",
        "🍊 الحصاد: اجمع الثمار عند اكتمال اللون البرتقالي — لا تتركها زيادة عالشجرة."
    ]
}

# ======================
# قوائم الواجهة
# ======================
def get_main_menu():
    keyboard = [
        [KeyboardButton("🤖 الاستعانة بالذكاء الاصطناعي"), KeyboardButton("🌾 المحاصيل")],
        [KeyboardButton("🌦 الطقس الحالي"), KeyboardButton("📅 توقعات 3 أيام")],
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
# دوال الطقس
# ======================
def fetch_weather_by_coords(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ar"
    try:
        r = requests.get(url)
        data = r.json()
        if data.get("cod") != 200:
            return "❌ لم أتمكن من جلب الطقس حالياً."
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        city = data["name"]
        return f"🌍 الموقع: {city}\n🌡 الحرارة: {temp}°C\n☁️ الحالة: {desc}"
    except Exception:
        return "⚠️ خطأ في الاتصال بموقع الطقس."

def fetch_forecast_by_coords(lat, lon, days=3):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts,current&appid={OPENWEATHER_API_KEY}&units=metric&lang=ar"
    try:
        r = requests.get(url)
        data = r.json()
        if "daily" not in data:
            return "❌ لم أتمكن من جلب توقعات الأيام القادمة."
        text = "📅 توقعات الطقس للأيام القادمة:\n\n"
        for i, day in enumerate(data["daily"][:days]):
            temp_min = day["temp"]["min"]
            temp_max = day["temp"]["max"]
            desc = day["weather"][0]["description"]
            text += f"اليوم {i+1}:\n🌡 الصغرى: {temp_min}°C — الكبرى: {temp_max}°C\n☁️ {desc}\n\n"
        return text
    except Exception:
        return "⚠️ خطأ في الاتصال بموقع الطقس."

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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["last_choice"] = text

    if text == "🌾 المحاصيل":
        await update.message.reply_text("📋 اختر المحصول:", reply_markup=get_crops_menu())
    elif text in crops:
        advices = crop_advices.get(text, [])
        response = f"📌 نصائح لـ {text}:\n\n" + "\n".join([f"- {a}" for a in advices])
        await update.message.reply_text(response, reply_markup=get_crops_menu())
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
# إرسال التنبيهات اليومية
# ======================
async def daily_job(app: Application):
    for chat_id in subscribers:
        msg = random.choice([
            fetch_weather_by_coords(35.5, 35.8),  # يمكن تعديل الإحداثيات حسب الحاجة
            f"🌱 نصيحة زراعية: {random.choice(random_tips)}"
        ])
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
