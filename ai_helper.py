import os
from dotenv import load_dotenv
import openai

load_dotenv()  # تحميل ملف .env
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_ai(question, crop=None):
    """
    يرسل السؤال إلى نموذج الذكاء الاصطناعي ويعيد الرد كنص.
    """
    try:
        system_prompt = "أنت خبير زراعي تقدم نصائح مختصرة وواضحة للمزارعين."
        if crop:
            system_prompt = f"أنت خبير زراعي مختص بمحصول {crop}. قدم إجابة عملية ومباشرة للمزارع."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.7
        )

        answer = response.choices[0].message["content"].strip()
        return answer

    except Exception as e:
        return f"⚠️ حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}"
