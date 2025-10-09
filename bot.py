import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler

from advice import crops, crop_advices, get_random_tip
from weather import fetch_weather_by_coords, fetch_forecast_by_coords
from ai_helper import ask_ai
from investment_helper import calculate_profit
from investment_data import investment_examples

# ======================
# Load environment variables
# ======================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN غير محدد!")

# ======================
# Setup logging and subscribers
# ======================
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
subscribers = set()

# ======================
# Define UI menus
# ======================
def get_main_menu():
    keyboard = [
        [KeyboardButton("🤖 الاستعانة بالذكاء الصناعي"), KeyboardButton("🌾 المحاصيل")],
        [KeyboardButton("📅 توقعات 3 أيام"), KeyboardButton("🌦 الطقس الحالي")],
        [KeyboardButton("🗺 الخرائط الزراعية"), KeyboardButton("💰 الاستثمار المتوقع")],
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

def get_investment_menu():
    rows = []
    crops_list = list(investment_examples.keys())
    for i in range(0, len(crops_list), 2):
        row = crops_list[i:i+2]
        rows.append([KeyboardButton(c) for c in row])
    rows.append([KeyboardButton("⬅️ رجوع للقائمة")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def get_ai_menu():
    """Return AI chat menu with back button"""
    keyboard = [
        [KeyboardButton("⬅️ رجوع للقائمة")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ======================
# Bot commands
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
# Handle messages
# ======================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["last_choice"] = text

    # ---------- AI chat mode ----------
    if context.user_data.get("ai_chat"):
        if text == "⬅️ رجوع للقائمة":
            # Exit AI chat mode
            context.user_data["ai_chat"] = False
            await update.message.reply_text("⬅️ عدت للقائمة الرئيسية.", reply_markup=get_main_menu())
        else:
            # Respond to AI question
            await update.message.reply_text("⏳ جاري التفكير...")
            try:
                reply = ask_ai(text)
                await update.message.reply_text(reply, reply_markup=get_ai_menu())
            except Exception as e:
                await update.message.reply_text(f"⚠️ حدث خطأ أثناء الاتصال بالذكاء الصناعي: {e}", reply_markup=get_ai_menu())
        return

    # ---------- User pressed AI button ----------
    if text == "🤖 الاستعانة بالذكاء الصناعي":
        context.user_data["ai_chat"] = True
        await update.message.reply_text(
            "💬 أرسل سؤالك الزراعي وسأجيبك بالذكاء الصناعي.\nاضغط '⬅️ رجوع للقائمة' للعودة للقائمة الرئيسية.",
            reply_markup=get_ai_menu()
        )
        return
    # --------------------------------------

    # ---------- Investment ----------
    if text == "💰 الاستثمار المتوقع":
        await update.message.reply_text("💰 اختر المحصول للاستثمار:", reply_markup=get_investment_menu())
        context.user_data["awaiting_investment_choice"] = True
        return

    if context.user_data.get("awaiting_investment_choice"):
        if text in investment_examples:
            context.user_data["selected_investment_crop"] = text
            context.user_data["awaiting_investment_choice"] = False
            context.user_data["awaiting_area_input"] = True
            await update.message.reply_text("📏 أدخل مساحة الأرض بالدونم (رقم فقط):")
            return

    if context.user_data.get("awaiting_area_input"):
        try:
            area = float(text)
            crop_name = context.user_data.get("selected_investment_crop")
            profit_text = calculate_profit(crop_name, area)
            await update.message.reply_text(profit_text, reply_markup=get_main_menu())
        except Exception:
            await update.message.reply_text("❌ يرجى إدخال رقم صحيح للمساحة.", reply_markup=get_main_menu())
        finally:
            context.user_data["awaiting_area_input"] = False
        return

    # ---------- Crops ----------
    if text == "🌾 المحاصيل":
        await update.message.reply_text("📋 اختر المحصول:", reply_markup=get_crops_menu())
    elif text in crops:
        info = crop_advices.get(text, {})
        if info:
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

    # ---------- Weather ----------
    elif text == "🌦 الطقس الحالي":
        await update.message.reply_text("📍 أرسل موقعك للحصول على الطقس الحالي:", reply_markup=get_weather_menu())
    elif text == "📅 توقعات 3 أيام":
        await update.message.reply_text("📍 أرسل موقعك للحصول على توقعات الطقس لـ 3 أيام:", reply_markup=get_weather_menu())

    # ---------- Maps ----------
    elif text == "🗺 الخرائط الزراعية":
        await update.message.reply_text("🗺 ميزة الخرائط الزراعية قيد التطوير 🚧", reply_markup=get_main_menu())

    # ---------- Return to main menu ----------
    elif text == "⬅️ رجوع للقائمة":
        await update.message.reply_text("⬅️ رجعت للقائمة الرئيسية.\nاختر من جديد:", reply_markup=get_main_menu())

    # ---------- Any other message ----------
    else:
        await update.message.reply_text("❌ لم أفهم رسالتك، اختر من القائمة.", reply_markup=get_main_menu())

# ======================
# Handle location
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
# Daily notifications
# ======================
async def daily_job(app: Application):
    for chat_id in subscribers:
        msg = get_random_tip()
        try:
            await app.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            logging.error(f"Error sending to {chat_id}: {e}")

def start_scheduler(app: Application):
    scheduler = BackgroundScheduler(timezone="Asia/Damascus")
    scheduler.add_job(lambda: asyncio.create_task(daily_job(app)), trigger="cron", hour=8, minute=0)
    scheduler.start()

# ======================
# Run bot
# ======================
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))

    start_scheduler(app)

    print("✅ البوت يعمل — استعد لاستقبال الرسائل.")
    app.run_polling()

if __name__ == "__main__":
    main()
