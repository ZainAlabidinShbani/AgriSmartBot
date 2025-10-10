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

    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ar"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        if data.get("cod") != "200":
            msg = data.get("message", "خطأ غير معروف")
            return f"❌ لم أتمكن من جلب توقعات الأيام القادمة.\n🔹 السبب: {msg}"

        # forecast يحتوي على قراءات كل 3 ساعات — نجمعها حسب الأيام
        from datetime import datetime
        from collections import defaultdict

        daily_data = defaultdict(list)
        for item in data["list"]:
            date = datetime.fromtimestamp(item["dt"]).date()
            temp = item["main"]["temp"]
            humidity = item["main"]["humidity"]
            wind = item["wind"]["speed"]
            desc = item["weather"][0]["description"]
            daily_data[date].append((temp, humidity, wind, desc))

        # إعداد النص النهائي
        text = "📅 توقعات الطقس للأيام القادمة:\n\n"
        for i, (date, values) in enumerate(sorted(daily_data.items())[:days]):
            temps = [v[0] for v in values]
            hums = [v[1] for v in values]
            winds = [v[2] for v in values]
            descs = [v[3] for v in values]
            avg_desc = max(set(descs), key=descs.count)

            text += (
                f"📆 {date.strftime('%A %d/%m')}:\n"
                f"🌡 الصغرى: {min(temps):.1f}°C — الكبرى: {max(temps):.1f}°C\n"
                f"💧 الرطوبة المتوسطة: {sum(hums)//len(hums)}%\n"
                f"🌬️ الرياح المتوسطة: {sum(winds)/len(winds):.1f} م/ث\n"
                f"☁️ الحالة الغالبة: {avg_desc}\n\n"
            )

        return text.strip()

    except requests.exceptions.RequestException:
        return "⚠️ تعذر الاتصال بخدمة التوقعات، حاول لاحقاً."
    except Exception as e:
        return f"⚠️ حدث خطأ غير متوقع أثناء جلب التوقعات: {e}"

