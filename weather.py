import requests
import os

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def check_api_key():
    if not OPENWEATHER_API_KEY:
        return "❌ لم يتم ضبط مفتاح OpenWeather API في الإعدادات."
    return None

def fetch_weather_by_coords(lat, lon):
    err = check_api_key()
    if err:
        return err

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ar"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        if data.get("cod") != 200:
            return f"❌ لم أتمكن من جلب الطقس حالياً.\n🔹 رمز الخطأ: {data.get('message', 'غير معروف')}"

        temp = data["main"]["temp"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        desc = data["weather"][0]["description"]
        city = data.get("name", "موقعك الحالي")

        return (
            f"🌍 الموقع: {city}\n"
            f"🌡 الحرارة: {temp:.1f}°C (⬆️ {temp_max:.1f}°C / ⬇️ {temp_min:.1f}°C)\n"
            f"💧 الرطوبة: {humidity}%\n"
            f"🌬️ الرياح: {wind_speed} م/ث\n"
            f"☁️ الحالة: {desc}"
        )

    except requests.exceptions.RequestException:
        return "⚠️ تعذر الاتصال بخدمة الطقس، تحقق من الإنترنت أو أعد المحاولة لاحقاً."
    except Exception as e:
        return f"⚠️ حدث خطأ غير متوقع: {e}"


def fetch_forecast_by_coords(lat, lon, days=3):
    err = check_api_key()
    if err:
        return err

    # تحديث إلى واجهة One Call 3.0
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts,current&appid={OPENWEATHER_API_KEY}&units=metric&lang=ar"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        if "daily" not in data:
            msg = data.get("message", "لم يتم العثور على بيانات الطقس.")
            return f"❌ لم أتمكن من جلب توقعات الأيام القادمة.\n🔹 السبب: {msg}"

        text = "📅 توقعات الطقس للأيام القادمة:\n\n"
        for i, day in enumerate(data["daily"][:days]):
            temp_min = day["temp"]["min"]
            temp_max = day["temp"]["max"]
            desc = day["weather"][0]["description"]
            humidity = day["humidity"]
            wind_speed = day["wind_speed"]
            text += (
                f"📆 اليوم {i+1}:\n"
                f"🌡 الصغرى: {temp_min:.1f}°C — الكبرى: {temp_max:.1f}°C\n"
                f"💧 الرطوبة: {humidity}%\n"
                f"🌬️ الرياح: {wind_speed} م/ث\n"
                f"☁️ {desc}\n\n"
            )
        return text.strip()

    except requests.exceptions.RequestException:
        return "⚠️ تعذر الاتصال بخدمة التوقعات، حاول لاحقاً."
    except Exception as e:
        return f"⚠️ حدث خطأ غير متوقع أثناء جلب التوقعات: {e}"
