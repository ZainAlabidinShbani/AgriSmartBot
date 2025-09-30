from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# التوكن مباشرة
TELEGRAM_TOKEN = "8211953729:AAGp9UVapIdIPbiwCrYl-Ut63qerlTdVjbI"

# قائمة المحاصيل السورية
crops = ["قمح", "زيتون", "قطن", "عنب", "حمضيات"]

# قاعدة بيانات نصائح محسنة
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

# القائمة الرئيسية
def get_main_menu():
    keyboard = [
        [KeyboardButton("🌾 المحاصيل")],
        [KeyboardButton("🤖 الاستعانة بالذكاء الاصطناعي")],
        [KeyboardButton(" توقعات الطقس"), KeyboardButton(" الخرائط الزراعية")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# قائمة المحاصيل
def get_crops_menu():
    keyboard = [[KeyboardButton(crop)] for crop in crops]
    keyboard.append([KeyboardButton("⬅️ رجوع للقائمة")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👨‍🌾 أهلاً بك! اختر من القائمة:", reply_markup=get_main_menu())

# استقبال الرسائل (من الكيبورد)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🌾 المحاصيل":
        await update.message.reply_text("📋 اختر المحصول:", reply_markup=get_crops_menu())

    elif text in crops:
        advices = crop_advices.get(text, [])
        response = f"📌 نصائح لـ {text}:\n\n" + "\n".join([f"- {advice}" for advice in advices])
        await update.message.reply_text(response, reply_markup=get_crops_menu())

    elif text == "🤖 الاستعانة بالذكاء الاصطناعي":
        await update.message.reply_text("🚧 ميزة الذكاء الاصطناعي غير مفعلة حالياً.", reply_markup=get_main_menu())

    elif text == "🌦 توقعات الطقس":
        await update.message.reply_text("🌦 ميزة توقعات الطقس قيد التطوير 🚧", reply_markup=get_main_menu())

    elif text == "🗺 الخرائط الزراعية":
        await update.message.reply_text("🗺 ميزة الخرائط الزراعية قيد التطوير 🚧", reply_markup=get_main_menu())

    elif text == "⬅️ رجوع للقائمة":
        await update.message.reply_text("⬅️ رجعت للقائمة الرئيسية.\nاختر من جديد:", reply_markup=get_main_menu())

# main
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("menu", start))

    # استقبال النصوص من الكيبورد
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ البوت يعمل — استعد لاستقبال الرسائل (ReplyKeyboard).")
    app.run_polling()

if __name__ == "__main__":
    main()
