import requests
import os

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def fetch_weather_by_coords(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ar"
    try:
        r = requests.get(url)
        data = r.json()
        if data.get("cod") != 200:
            return "❌ لم أتمكن من جلب الطقس حالياً."

        temp = data["main"]["temp"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        desc = data["weather"][0]["description"]
        city = data["name"]

        return (
            f"🌍 الموقع: {city}\n"
            f"🌡 الحرارة: {temp}°C (⬆️ {temp_max}°C / ⬇️ {temp_min}°C)\n"
            f"💧 الرطوبة: {humidity}%\n"
            f"🌬️ الرياح: {wind_speed} م/ث\n"
            f"☁️ الحالة: {desc}"
        )
    except Exception:
        return "⚠️ خطأ في الاتصال بموقع الطقس."

def fetch_forecast_by_coords(lat, lon, days=7):
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts,current&appid={OPENWEATHER_API_KEY}&units=metric&lang=ar"
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
            humidity = day["humidity"]
            wind_speed = day["wind_speed"]
            text += (
                f"اليوم {i+1}:\n"
                f"🌡 الصغرى: {temp_min}°C — الكبرى: {temp_max}°C\n"
                f"💧 الرطوبة: {humidity}%\n"
                f"🌬️ الرياح: {wind_speed} م/ث\n"
                f"☁️ {desc}\n\n"
            )
        return text
    except Exception:
        return "⚠️ خطأ في الاتصال بموقع الطقس."
