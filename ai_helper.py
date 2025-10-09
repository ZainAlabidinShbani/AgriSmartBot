import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# ============================================================
# 🟢 تحميل ملف البيئة (.env) من نفس مجلد المشروع
# ============================================================
# هذه الخطوة ضرورية لقراءة المفاتيح (API Keys) الموجودة في الملف .env
# إذا لم يتم تحميله، الكود لن يجد مفاتيح Azure OpenAI
basedir = os.path.dirname(__file__)
load_dotenv(os.path.join(basedir, ".env"))

# ============================================================
# 🟢 قراءة متغيرات البيئة الخاصة بـ Azure OpenAI
# ============================================================
# يتم جلب القيم من ملف .env أو من النظام (في حال كانت مضبوطة هناك)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://signalml.openai.azure.com/")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")  # تأكد من الاسم مطابق تماماً لما في .env
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-mini")

# ============================================================
# 🟢 فحص المفتاح قبل إنشاء العميل (تشخيص مبسط)
# ============================================================
if not AZURE_OPENAI_API_KEY:
    raise RuntimeError("❌ لم يتم العثور على المفتاح AZURE_OPENAI_API_KEY. تأكد من وجوده في ملف .env")

# ============================================================
# 🟢 إنشاء عميل Azure OpenAI
# ============================================================
# هذا الكائن هو الذي يرسل الطلبات إلى واجهة Azure OpenAI
client = AzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
)

# ============================================================
# 🧠 الدالة الرئيسية للتفاعل مع الذكاء الاصطناعي
# ============================================================
def ask_ai(question, crop=None):
    """
    ترسل السؤال إلى نموذج Azure OpenAI وتعيد الرد كنص.
    """
    try:
        # تخصيص النغمة (حسب وجود المحصول)
        system_prompt = "أنت خبير زراعي تقدم نصائح مختصرة وواضحة للمزارعين."
        if crop:
            system_prompt = f"أنت خبير زراعي مختص بمحصول {crop}. قدم إجابة عملية ومباشرة للمزارع."

        # إرسال الطلب إلى Azure OpenAI
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ]
            # بدون temperature أو max_tokens لأن gpt-5-mini ما بيدعمها
        )

        # ✅ التأكد من وجود رد فعلي
        if not response or not response.choices:
            return "⚠️ لم أتلقَّ أي رد من نموذج الذكاء الاصطناعي."

        # ✅ كائن الرسالة الجديد من نوع ChatCompletionMessage
        message = response.choices[0].message

        # ✅ الوصول إلى النص من الخاصية .content (وليس get)
        if not message or not hasattr(message, "content") or not message.content:
            return "⚠️ النموذج لم يُرجع أي نص في الرد."

        # ✅ استخراج النص الفعلي
        answer = message.content.strip()

        # تسجيل الرد في الكونسول للمراقبة
        print("🧠 رد الذكاء الاصطناعي:", answer)

        return answer if answer else "⚠️ لم أتمكن من توليد إجابة مناسبة."

    except Exception as e:
        return f"⚠️ حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}"
