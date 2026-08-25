# SAYYOD Bot - ISPU SAT Rasmiy Telegram Boti

## O'rnatish

1. Python 3.7+ o'rnatilgan bo'lishi kerak

2. Kerakli kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

3. `.env` faylini to'ldiring:
```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
BOT_USERNAME=YOUR_BOT_USERNAME
SUPABASE_URL=YOUR_SUPABASE_URL
SUPABASE_KEY=YOUR_SUPABASE_ANON_KEY
```

4. Botni ishga tushiring:
```bash
python bot.py
```

## Bot funksiyalari

### 📱 Kod tasdiqlash
- `/start verify_901234567` — Deep link orqali kod yuborish
- "📱 Raqamni tasdiqlash" tugmasi — Qo'lda kod olish
- 4 xonali tasdiqlash kodi
- Supabase database ga kod saqlash

### ℹ️ Ma'lumotlar
- ISPU haqida ma'lumot
- Bog'lanish ma'lumotlari

## Ishlash tartibi

```
Website → Foydalanuvchi telefon kiraydi → "Kod yuborish" tugmasi
    ↓
Telegram bot ochiladi → /start verify_901234567
    ↓
Bot 4 xonali kod yaratadi → Supabase ga saqlaydi → Foydalanuvchiga ko'rsatadi
    ↓
Foydalanuvchi kodni website ga kiraydi → Supabase dan tekshiriladi
```

## Fayl tuzilishi

```
sayyod/
├── bot.py              # Asosiy bot fayli
├── config.py           # Sozlamalar (Supabase + Bot)
├── handlers.py         # Asosiy handlerlar
├── keyboards.py        # Tugmalar
├── verification.py     # Kod tasdiqlash (Supabase bilan)
├── .env               # Maxfiy kalitlar (git ga qo'shmaslik!)
├── requirements.txt    # Kutubxonalar
└── README.md          # Bu fayl
```

## Database

Bot quyidagi Supabase jadvallarini ishlatadi:
- `verification_codes` — Tasdiqlash kodlari
- `user_profiles` — Foydalanuvchi profillari

## Xavfsizlik

- `.env` faylini hech qachon git ga qo'shmang!
- Bot token va Supabase key sir saqlang
- Production da `SUPABASE_KEY` ni faqat anon key ishlating
