from telegram import ReplyKeyboardMarkup, KeyboardButton
from advice import crops
from investment_data import investment_examples  # استيراد المحاصيل الاستثمارية

def get_main_menu():
    keyboard = [
        [KeyboardButton("🤖 الاستعانة بالذكاء الاصطناعي"), KeyboardButton("🌾 المحاصيل")],
        [KeyboardButton("📅 توقعات 3 أيام"), KeyboardButton("🌦 الطقس الحالي")],
        [KeyboardButton("🗺 الخرائط الزراعية"), KeyboardButton("💰 الاستثمار المتوقع")],  # زر جديد
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
    """
    قائمة المحاصيل الخاصة بالاستثمار.
    """
    rows = []
    from investment_data import investment_examples
    crops_list = list(investment_examples.keys())
    for i in range(0, len(crops_list), 2):
        row = crops_list[i:i+2]
        rows.append([KeyboardButton(c) for c in row])
    rows.append([KeyboardButton("⬅️ رجوع للقائمة")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)
