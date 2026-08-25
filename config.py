import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME", "SAYY0D_BOT")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# OpenRouter AI
AI_API_KEY = os.getenv("AI_API_KEY")
AI_API_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "google/gemini-2.5-flash"

# Admin
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")

# Kerakli env varlarni tekshirish
_missing = []
if not BOT_TOKEN: _missing.append("BOT_TOKEN")
if not SUPABASE_URL: _missing.append("SUPABASE_URL")
if not SUPABASE_KEY: _missing.append("SUPABASE_KEY")
if not SUPABASE_SERVICE_KEY: _missing.append("SUPABASE_SERVICE_KEY")
if not AI_API_KEY: _missing.append("AI_API_KEY")
if _missing:
    print(f"ETISHLIMIY ENV VARLAR: {', '.join(_missing)}")
    print(f".env fayl: {os.path.abspath('.env')}")

# ISPU ma'lumotlari
ISPU_INFO = {
    "name": "ISPU — International SAT Platform Uzbekistan",
    "website": "https://ispu.uz",
    "description": "Digital SAT tayyorgarlik platformasi",
    "phone": "+998 88 111 22 71",
    "telegram": "@yahyobeknormurodov",
    "telegram_group": "@SATeducational",
    "instagram": "https://www.instagram.com/ispu_inc",
    "youtube": "https://youtube.com/@ispu-sat",
    "address": "Toshkent shahri, O'zbekiston"
}

ISPU_ABOUT = """
🎓 <b>ISPU — International SAT Platform Uzbekistan</b>

ISPU — O'zbekistondagi o'quvchilar uchun yaratilayotgan zamonaviy Digital SAT tayyorgarlik platformasi.

🎯 <b>Asosiy maqsad:</b>
SAT imtihoniga tayyorgarlikni o'zbek o'quvchilari uchun qulay, tizimli, interaktiv va texnologik qilish.

📚 <b>Asosiy bo'limlar:</b>
• 📖 Lessons — SAT mavzularini video va interaktiv darslar orqali o'rganish
• 📝 Modules — Alohida mavzular bo'yicha mashqlar bajarish
• 🧪 Mock Test — To'liq Digital SAT formatida sinov imtihonlari

🤖 <b>AI Tahlilchi:</b>
AI o'quvchining test natijalari va xatolarini tahlil qilib, bilimdagi bo'shliqlarni aniqlashga yordam beradi.

👨‍🏫 <b>Mentor tizimi:</b>
Mentorlar o'quvchining rivojlanishini kuzatishi va tavsiyalar berishi mumkin.

🔄 <b>O'rganish jarayoni:</b>
Learn → Practice → Test → Analyze → Improve

🌐 <b>Veb-sayt:</b> ispu.uz
📱 <b>Telegram guruh:</b> @SATeducational
📸 <b>Instagram:</b> @ispu_inc
🎬 <b>YouTube:</b> @ispu-sat
📅 <b>Ishga tushirilishi:</b> 2026-yil sentabr
"""

# To'lov ma'lumotlari
PAYMENT_CARD = "446613695053733"
PAYMENT_CARD_OWNER = "Y.N"

# VIP tariflari
VIP_SOLO_PRICE = "20,000 so'm/oy"
VIP_PRO_PRICE = "45,000 so'm/oy"
VIP_FREE_UNTIL = "1 oktyabr 2026"

# Bepul cheklovlar
FREE_MOCK_LIMIT = 3
FREE_MODULE_LIMIT = 12
FREE_LESSON_LIMIT = 1
