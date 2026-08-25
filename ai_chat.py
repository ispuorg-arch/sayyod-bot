import httpx
from telegram import Update
from telegram.ext import ContextTypes
from config import AI_API_KEY, AI_API_URL, AI_MODEL

# 100 ta ISPU/SAT savol-javob
QA_DATABASE = {
    # ══════════════════════════════════════════════
    # ISPU PLATFORMASI HAQIDA (1-15)
    # ══════════════════════════════════════════════
    "ispu nima": "ISPU — International SAT Platform Uzbekistan. Bu O'zbekistondagi birinchi to'liq raqamli SAT tayyorgarlik platformasi. ispu.uz da ishlaydi.",
    "ispu haqida": "ISPU — O'zbekistondagi Digital SAT tayyorgarlik platformasi. Biz SAT imtihoniga tayyorlanish uchun barcha kerakli vositalarni taqdim etamiz: darslar, mock testlar, AI tahlil va mentor yordami.",
    "ispu nima uchun": "ISPU O'zbek o'quvchilari uchun SAT tayyorgarlikni qulay va hamyonbop qilish maqsadida yaratilgan. Maqsadimiz — har bir o'quvchiga sifatli ta'lim berish.",
    "ispu qachon yaratilgan": "ISPU 2026-yil sentabr oyida ishga tushirilgan.",
    "ispu kim tomonidan yaratilgan": "ISPU Yahyobek Normurodov (@yahyobeknormurodov) tomonidan yaratilgan.",
    "ispu manzili": "ISPU markazi Toshkent shahrida, O'zbekistonda joylashgan.",
    "ispu telefon": "Bizning telefon: +998 88 111 22 71",
    "ispu telegram": "Bizning Telegram: @yahyobeknormurodov",
    "ispu instagram": "Bizning Instagram: https://www.instagram.com/ispu_inc",
    "ispu youtube": "Bizning YouTube kanal: https://youtube.com/@ispu-sat",
    "ispu sayt": "Bizning sayt: https://ispu.uz",
    "ispu guruh": "Bizning Telegram guruh: @SATeducational",
    "ispu qanday ishlaydi": "Ro'yxatdan o'ting → Darslarni o'rganing → Mashq qiling → Test topshiring → AI tahlilini ko'ring. O'rganish jarayoni: Learn → Practice → Test → Analyze → Improve.",
    "ispu boshqa mamlakatlar": "Hozircha faqat O'zbekistonda ishlaymiz. Kelajakda boshqa mamlakatlarga ham chiqishni rejalashtirmoqdamiz.",
    "ispu tillari": "Platforma o'zbek va rus tillarida ishlaydi.",

    # ══════════════════════════════════════════════
    # RO'YXATDAN O'TISH (16-25)
    # ══════════════════════════════════════════════
    "ro'yxatdan o'tish": "Botdagi /start ni bosing → 'Ro'yxatdan o'tish' tugmasini bosing → Ism, familiya, telefon, login, parol kiriting. Saytda ispu.uz ga kiring va kirish.",
    "qanday ro'yxatdan o'tish": "Telegram botda /start yozing, 'Ro'yxatdan o'tish' tugmasini bosing. Keyin ismingiz, familiyangiz, telefon raqamingiz, login va parolni kiriting.",
    "ro'yxatdan o'tish mumkin emas": "Muammo bo'lsa, admin bilan bog'laning: @yahyobeknormurodov",
    "login nima": "Login — bu sizning ismingiz yoki taxallusingiz. Kamida 4 ta belgi, faqat harflar va raqamlar bo'lishi kerak. Masalan: ahmad123",
    "parol nima": "Parol — sizning maxfiy kalshingiz. Kamida 6 ta belgi bo'lishi kerak. Maxfiy saqlang!",
    "login o'zgartirish": "Hozircha login o'zgartirib bo'lmaydi. Yangi hisob yaratishingiz mumkin.",
    "parolni unutdim": "Admin bilan bog'laning: @yahyobeknormurodov — parolni tiklashga yordam beradi.",
    "hisobimni o'chirish": "Admin bilan bog'laning: @yahyobeknormurodov — hisobingizni o'chirib beradi.",
    "ikkinchi hisob": "Bitta Telegram ID bilan faqat bitta hisob yaratish mumkin.",
    "ro'yxatdan o'tish bepul": "Ha, ro'yxatdan o'tish mutlaqo bepul!",

    # ══════════════════════════════════════════════
    # VIP OBUNA (26-40)
    # ══════════════════════════════════════════════
    "vip nima": "VIP obuna — premium xizmat. Cheksiz mock test, cheksiz modul, barcha darslar va AI tahlilchi mavjud.",
    "vip narxi": "Ikki tur bor: Solo — 20,000 so'm/oy (1 kishi), Pro — 45,000 so'm/oy (3 kishi).",
    "solo nima": "Solo tarif — 20,000 so'm/oy. Faqat bitta kishi uchun. Cheksiz mock test, modul va AI tahlil.",
    "pro nima": "Pro tarif — 45,000 so'm/oy. 3 kishi foydalanishi mumkin (25% tejamkorlik). Hamma narsa ochiq.",
    "bepul nima beradi": "Bepul: 3 ta mock test, 12 ta modul, 1 ta dars. 1 oktyabrgacha bepul!",
    "vip qachon tugaydi": "Obuna muddati tugagandan keyin avtomatik bepul tarifga qaytadi.",
    "vip to'lash": "Kartaga o'tkazish: 446613695053733 (Y.N). To'lov rasmini botga yuboring.",
    "vip tasdiqlash": "To'lov rasmini yuborgandan keyin admin tasdiqlaydi. 1-2 soat ichida.",
    "vip boshlash": "Ro'yxatdan o'ting → VIP obuna tugmasini bosing → Tarifni tanlang → To'lovni amalga oshiring.",
    "vip bekor qilish": "Admin bilan bog'laning: @yahyobeknormurodov",
    "vip muddati": "Obuna 1 oy muddatga beriladi.",
    "vip 3 kishi": "Pro tarifda 3 ta hisob bir tekis foydalanishi mumkin.",
    "vip farqi": "Bepul: cheklangan. VIP: cheksiz barcha imkoniyatlar.",
    "vip yangilash": "Obuna muddati tugagandan keyin qayta to'lang.",
    "vip sinov": "1 oktyabrgacha barcha funksiyalar bepul!",

    # ══════════════════════════════════════════════
    # SAT IMTIHONI (41-60)
    # ══════════════════════════════════════════════
    "sat nima": "SAT — Scholastic Assessment Test. AQSh universitetlariga kirish uchun topshiriladigan standartlashtirilgan imtihon.",
    "sat qanday imtihon": "Digital SAT — kompyuterda topshiriladigan imtihon. Reading & Writing (64 savol, 64 daqiqa) va Math (44 savol, 70 daqiqa).",
    "sat ball": "Ball: 400-1600. Har bir bo'lim uchun 200-800 ball.",
    "sat reading": "Reading & Writing — O'qish va yozish. 64 savol, 64 daqiqa. 200-800 ball.",
    "sat math": "Math — Matematika. 44 savol, 70 daqiqa. 200-800 ball.",
    "sat necha soat": "Jami: 64 + 70 = 134 daqiqa (taxminan 2 soat 14 daqiqa).",
    "sat necha savol": "Jami: 64 + 44 = 108 savol.",
    "sat qachon": "SAT imtihonlari yiliga bir necha marta o'tkaziladi. Kelgusi imtihonlar haqida: https://collegeboard.org",
    "sat qayerda": "AQSh va boshqa mamlakatlardagi test markazlarida. O'zbekistonda ham o'tkazilishi mumkin.",
    "sat tayyorgarlik": "ISPU platformasidan foydalaning! Darslarni o'rganing, mock testlarni yeching, AI tahlilini ko'ring.",
    "sat osonmi": "Qiyinlik darajasi o'rtacha. Tayyorgarlik bilan yuqori ball olish mumkin.",
    "sat qiyinmi": "Tayyorgarlik bilan qiyin emas. ISPU platformasi sizga yordam beradi!",
    "sat eng yuqori ball": "Eng yuqori ball: 1600 (800 Reading + 800 Math).",
    "sat eng past ball": "Eng past ball: 400 (200 Reading + 200 Math).",
    "sat passing score": "O'rtacha ball: 1050. Yaxshi ball: 1200+. Ajoyib: 1400+.",
    "sat universitet": "SAT balli AQSh, Kanada, Buyuk Britaniya va boshqa mamlakatlardagi universitetlarga kirish uchun qabul qilinadi.",
    "sat hozir qachon": "2026-yil oxirida va 2027-yil boshida imtihonlar bo'lishi mumkin. Aniq sanalar: https://collegeboard.org",
    "sat ro'yxatdan o'tish": "Collegeboard.org saytida ro'yxatdan o'ting.",
    "sat to'lov": "Collegeboard.org orqali to'lang. Narx: taxminan $60.",
    "sat bepul": "Ha, ISPU platformasida SAT tayyorgarlik bepul (1 oktyabrgacha)!",

    # ══════════════════════════════════════════════
    # DARSLAR VA MODULLAR (61-75)
    # ══════════════════════════════════════════════
    "darslar": "Platformada SAT mavzulari bo'yicha video va interaktiv darslar mavjud.",
    "modullar": "Alohida mavzular bo'yicha mashqlar. 12 ta bepul modul mavjud.",
    "qanday o'rganish": "O'rganish jarayoni: Learn → Practice → Test → Analyze → Improve.",
    "darslar qancha": "Bepul: 1 ta dars. VIP: cheksiz darslar.",
    "modullar qancha": "Bepul: 12 ta modul. VIP: cheksiz modullar.",
    "darslar qanday": "Video va interaktiv darslar. O'z tezligingizda o'rganing.",
    "modullar qanday": "Mashq topshiriqlari. Bilimingizni tekshiring.",
    "math darslar": "Matematika bo'yicha barcha mavzular: algebra, geometriya, statistika va boshqalar.",
    "reading darslar": "O'qish va yozish bo'yicha darslar: grammatika, matn tahlili va boshqalar.",
    "writing darslar": "Yozish bo'yicha darslar: grammatika, tuzilma va boshqalar.",
    "darslar boshlangich": "Ha, darslar boshlang'ich darajadan boshlanadi.",
    "darslar murakkab": "Dastlab oddiy mavzular, keyin murakkab mavzular.",
    "darslar vaqti": "Har bir dars 5-15 daqiqa. O'z vaqtingizda o'rganing.",
    "darslar qachon": "Istalgan vaqtda! Platforma 24/7 ochiq.",
    "darslar qayerda": "ispu.uz saytida. Kompyuter yoki telefonda kirishingiz mumkin.",

    # ══════════════════════════════════════════════
    # MOCK TEST (76-85)
    # ══════════════════════════════════════════════
    "mock test": "To'liq Digital SAT formatida sinov imtihonlari. Haqiqiy imtihon sharoitida mashq qiling.",
    "mock test necha tadan": "Bepul: 3 ta mock test. VIP: cheksiz mock test.",
    "mock test qanday": "Haqiqiy SAT formatida: Reading & Writing + Math. Vaqt cheklangan.",
    "mock test natija": "Test tugagandan keyin AI tahlilini ko'ring. Kuchli va zaif tomonlaringizni bilib oling.",
    "mock test tayyorlanish": "Darslarni o'rganing → Modullarni bajaring → Mock testni topshiring.",
    "mock test qancha vaqt": "Reading & Writing: 64 daqiqa. Math: 70 daqiqa. Jami: taxminan 2 soat 14 daqiqa.",
    "mock test ball": "Mock test natijalari haqiqiy SAT balli kabi baholanadi.",
    "mock test xato": "Xatolaringizni tahlil qiling. AI yordamida tushunib oling.",
    "mock test takrorlash": "VIP da cheksiz takrorlashingiz mumkin.",
    "mock test bepul": "Ha, 3 ta mock test bepul!",

    # ══════════════════════════════════════════════
    # AI TAHLIL (86-92)
    # ══════════════════════════════════════════════
    "ai nima": "AI Tahlilchi — sun'iy intellekt sizning test natijalaringizni tahlil qiladi va shaxsiy tavsiyalar beradi.",
    "ai qanday ishlaydi": "Test topshirgandan keyin AI sizning javoblaringizni tahlil qiladi va kuchli/zaif tomonlaringizni ko'rsatadi.",
    "ai foydasi": "Shaxsiy o'rganish rejasi, kuchli va zaif tomonlar, yaxshilash yo'nalishlari.",
    "ai bepul mi": "Ha, AI tahlil barcha foydalanuvchilar uchun bepul.",
    "ai qanday": "Test tugagandan keyin 'AI tahlil' tugmasini bosing.",
    "ai yaxshimi": "Ha, AI juda aniq tahlil qiladi. O'rganish jarayoniga katta yordam beradi.",
    "ai savol": "AI ga istalgan savolingizni bering! SAT mavzularida yordam beradi.",

    # ══════════════════════════════════════════════
    # TO'LOV (93-98)
    # ══════════════════════════════════════════════
    "to'lov": "Kartaga o'tkazish: 446613695053733 (Y.N). To'lov rasmini botga yuboring.",
    "to'lov qanday": "1) Kartaga o'tkazing. 2) Rasmini botga yuboring. 3) Admin tasdiqlaydi.",
    "to'lov kartasi": "Karta raqami: 446613695053733, egasi: Y.N",
    "to'lov tasdiqlash": "To'lov rasmini yuborgandan keyin 1-2 soat ichida tasdiqlanadi.",
    "to'lov rad": "Agar to'lov noto'g'ri bo'lsa, admin sizga xabar beradi.",
    "to'lov qaytarish": "Admin bilan bog'laning: @yahyobeknormurodov",

    # ══════════════════════════════════════════════
    # UMUMIY SAVOLLAR (99-100)
    # ══════════════════════════════════════════════
    "rahmat": "Yordam bera olganimdan xursandman! Boshqa savolingiz bo'lsa, bemalol yozing! 😊",
    "salom": "Salom! ISPU AI yordamchisiga xush kelibsiz! SAT haqida qanday savolingiz bor? 😊",
    "qalaysiz": "Yaxshiman, rahmat! Siz qalaysiz? SAT tayyorgarlikda qanday yordam bera olaman? 😊",
    "yordam": "Albatta! SAT, ISPU, ro'yxatdan o'tish yoki boshqa mavzuda savolingiz bo'lsa, yozing!",
    "nima qilyapsiz": "Men ISPU AI yordamchisiman. Sizga SAT va ISPU haqida yordam bera olaman! 😊",
}

# System prompt
SYSTEM_PROMPT = """Sen ISPU AI yordamchisan. Sen foydalanuvchilarga SAT va ISPU haqida yordam berasan.

⚠️ ASOSIY QOIDALAR:
1. Agar savol QA_DATABASE da mavjud bo'lsa — O'SHA JAVOJNI QAYTAR (matnni aynan yoz, o'zgartirma)
2. Agar savol yo'q bo'lsa — o'z biliming bilan javob ber (lekin ISPU haqida ishonchli ma'lumot bilan)
3. Faqat O'zbek tilida javob ber
4. Qisqa va tushunarli javob ber
5. Do'stona va professional ohangda bo'lish

🚫 JAVOB BERMA (shu mavzularda so'rov kelsa):
- 18+ kontent (jinsiy, zo'ravonlik)
- Narkotika, alkogol haqida ma'lumot
- Noqonuniy harakatlar
- Boshqa odamlarga zarar yetkazish

Shu mavzularda javob ber:
"Kechirasiz, men bu mavzuda yordam bera olmayman. Boshqa savolingiz bo'lsa, bemalol yozing! 😊"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Nomi: ISPU — International SAT Platform Uzbekistan
🌐 Veb-sayt: https://ispu.uz
📱 Telefon: +998 88 111 22 71
💬 Telegram: @yahyobeknormurodov
👥 Telegram guruh: @SATeducational
📸 Instagram: https://www.instagram.com/ispu_inc
🎬 YouTube: https://youtube.com/@ispu-sat
📍 Manzil: Toshkent shahri, O'zbekiston
👨‍🏫 Asoschi: Yahyobek Normurodov (@yahyobeknormurodov)
📅 Ishga tushirilishi: 2026-yil sentabr

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VIP TARIFLARI:
• Solo: 20,000 so'm/oy (1 kishi) — Cheksiz mock test, AI, barcha darslar
• Pro: 45,000 so'm/oy (3 kishi, 25% tejamkorlik) — Hamma narsa ochiq
• Bepul: 1 oktyabrgacha sayt bepul!
• Bepul cheklovlar: 3 ta mock test, 12 ta modul, 1 ta dars

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLATFORMA BO'LIMLARI:
📖 Lessons — SAT mavzularini video va interaktiv darslar orqali o'rganish
📝 Modules — Alohida mavzular bo'yicha mashqlar
🧪 Mock Test — To'liq Digital SAT formatida sinov imtihonlari
🤖 AI Tahlilchi — Sun'iy intellekt test natijalarini tahlil qiladi

O'rganish jarayoni: Learn → Practice → Test → Analyze → Improve

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SAT IMTIHONI:
• Digital SAT — kompyuterda topshiriladi
• Reading & Writing: 64 savol, 64 daqiqa (200-800 ball)
• Math: 44 savol, 70 daqiqa (200-800 ball)
• Jami ball: 400-1600
• O'rtacha ball: 1050. Yaxshi: 1200+. Ajoyib: 1400+

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TO'LOV:
• Karta: 446613695053733 (Y.N)
• To'lov rasmini botga yuboring
• Admin tasdiqlashini kuting (1-2 soat)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Javoblarni qisqa va tushunarli yoz. Agar savol database da bo'lsa — o'sha javobni qaytar. Agar yo'q bo'lsa — o'z biliming bilan javob ber."""


def _find_best_answer(question: str) -> str:
    """Savolga eng mos javobni topish"""
    q = question.lower().strip()

    # To'g'ridan-to'g'ri moslik
    for key, answer in QA_DATABASE.items():
        if key in q or q in key:
            return answer

    # Qisqartma moslik (kalit so'zlar)
    keywords = {
        "ispu": ["ispu", "platforma", "sayt"],
        "ro'yxatdan o'tish": ["ro'yxatdan", "register", "qanday o'tish", "qanday ro'yxatdan"],
        "vip": ["vip", "obuna", "premium", "solo", "pro"],
        "sat": ["sat", "imtihon", "test topshirish", "ball"],
        "dars": ["dars", "o'rganish", "modul", "mashq"],
        "mock": ["mock", "sinov", "test"],
        "ai": ["ai", "sun'iy intellekt", "tahlil", "yordamchi"],
        "to'lov": ["to'lov", "pul", "karta", "o'tkazish"],
    }

    for category, words in keywords.items():
        for word in words:
            if word in q:
                # Kategoriya bo'yicha eng ko'p takrorlangan savolni qaytarish
                cat_answers = {k: v for k, v in QA_DATABASE.items() if any(w in k for w in words)}
                if cat_answers:
                    return list(cat_answers.values())[0]

    return None


async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """AI chat — ISPU/SAT mavzularida"""
    user_message = update.message.text

    # Avval database dan javob qidirish
    db_answer = _find_best_answer(user_message)

    if db_answer:
        try:
            await update.message.reply_text(db_answer)
        except Exception:
            pass
        return

    # Database da topilmasa — AI ga so'rov yuborish
    await update.message.reply_text("⏳ <b>O'ylayapman...</b>", parse_mode="HTML")

    try:
        headers = {
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": AI_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(AI_API_URL, json=payload, headers=headers)
            data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            ai_response = data["choices"][0]["message"]["content"]
            safe_response = ai_response.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            await update.message.reply_text(safe_response)
        else:
            await update.message.reply_text(
                "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring."
            )

    except httpx.TimeoutException:
        await update.message.reply_text(
            "⏳ Javo biroz kechikdi. Qaytadan urinib ko'ring.",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"AI xatolik: {e}")
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
            parse_mode="HTML"
        )
