from telegram import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard():
    """Ro'yxatdan o'tishdan oldin — barcha tugmalar"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("📝 Ro'yxatdan o'tish")],
        [KeyboardButton("💬 AI Yordamchi"), KeyboardButton("ℹ️ ISPU haqida")],
        [KeyboardButton("📞 Bog'lanish")]
    ], resize_keyboard=True)


def registered_keyboard():
    """Ro'yxatdan o'tgandan keyin"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("👤 Mening profilim"), KeyboardButton("📊 Holatim")],
        [KeyboardButton("💎 VIP obuna"), KeyboardButton("📚 Darslar")],
        [KeyboardButton("💬 AI Yordamchi"), KeyboardButton("📞 Bog'lanish")]
    ], resize_keyboard=True)


def phone_keyboard():
    """Telefon yuborish tugmasi"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("📱 Raqamni yuborish", request_contact=True)],
        [KeyboardButton("🔙 Orqaga")]
    ], resize_keyboard=True)


def back_keyboard():
    """Orqaga tugmasi"""
    return ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)


def confirm_keyboard():
    """Tasdiqlash tugmalari"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("✅ Tasdiqlash"), KeyboardButton("❌ Bekor qilish")]
    ], resize_keyboard=True)


def pro_tariff_keyboard():
    """Pro tariflar keyboard"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("💎 Solo — 20,000 so'm"), KeyboardButton("💎 Pro — 45,000 so'm")],
        [KeyboardButton("🔙 Orqaga")]
    ], resize_keyboard=True)


def payment_keyboard():
    """To'lov keyboard"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("💳 To'ladim")],
        [KeyboardButton("🔙 Orqaga")]
    ], resize_keyboard=True)


def payment_confirm_keyboard():
    """To'lov tasdiqlash keyboard"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("✅ Tasdiqlash"), KeyboardButton("❌ Bekor qilish")]
    ], resize_keyboard=True)


def admin_keyboard():
    """Admin keyboard"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("👥 Foydalanuvchilar"), KeyboardButton("📊 Statistika")],
        [KeyboardButton("📢 Xabar yuborish"), KeyboardButton("💳 To'lovlar")],
        [KeyboardButton("🔙 Orqaga")]
    ], resize_keyboard=True)
