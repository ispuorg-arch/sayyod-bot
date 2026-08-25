import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import PAYMENT_CARD, PAYMENT_CARD_OWNER, ADMIN_TELEGRAM_ID
from keyboards import payment_keyboard, payment_confirm_keyboard, back_keyboard
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

sb = create_client(SUPABASE_URL, SUPABASE_KEY)
logger = logging.getLogger(__name__)

WAITING_RECEIPT = "WAITING_RECEIPT"


async def payment_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """To'lov sahifasini ko'rsatish"""
    payment_text = (
        "💳 <b>To'lov</b>\n\n"
        "VIP obunaga o'tish uchun to'lov qiling:\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💳 <b>Karta raqami:</b>\n"
        f"<code>{PAYMENT_CARD}</code>\n\n"
        f"👤 <b>Egasi:</b> {PAYMENT_CARD_OWNER}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💎 <b>VIP tariflar:</b>\n"
        "• Solo — 20,000 so'm/oy (1 kishi)\n"
        "• Pro — 45,000 so'm/oy (3 kishi)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 <b>Qanday to'lash kerak:</b>\n"
        "1. Karta raqamini nusxalang\n"
        "2. O'z bankingizda pul o'tkazing\n"
        "3. Chek rasmini yuboring\n"
        "4. Admin tasdiqlashini kuting\n\n"
        "⚠️ <b>Muhim:</b> Chekda summa va sana ko'rinishi kerak!\n\n"
        "To'lovni amalga oshirdingizmi?"
    )
    await update.message.reply_text(
        payment_text,
        parse_mode="HTML",
        reply_markup=payment_keyboard()
    )


async def payment_made(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """To'ladim tugmasi bosilganda — chek so'rash"""
    await update.message.reply_text(
        "📸 <b>Chek yuboring</b>\n\n"
        "To'lov chekining rasmini yuboring.\n\n"
        "⚠️ <b>Talab qilinadi:</b>\n"
        "• Karta raqami ko'rinishi kerak\n"
        "• Summa ko'rinishi kerak\n"
        "• Sana va vaqt ko'rinishi kerak\n\n"
        "Rasm yuboring yoki bekor qilish uchun 🔙 Orqaga bosing.",
        parse_mode="HTML",
        reply_markup=back_keyboard()
    )
    context.user_data["payment_step"] = WAITING_RECEIPT
    return WAITING_RECEIPT


async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chek rasmni qabul qilish va adminga yuborish"""
    if not update.message.photo:
        await update.message.reply_text(
            "⚠️ Iltimos, rasm yuboring!\n\n"
            "Chek rasmini yuboring yoki 🔙 Orqaga bosing.",
            parse_mode="HTML",
            reply_markup=back_keyboard()
        )
        return WAITING_RECEIPT

    user = update.effective_user
    photo = update.message.photo[-1]  # Eng katta hajmli rasm

    # Foydalanuvchi ma'lumotlarini olish
    try:
        user_data = sb.table("ispu_users").select("*").eq("telegram_id", user.id).execute()
        if user_data.data:
            u = user_data.data[0]
            user_name = f"{u.get('ism', '?')} {u.get('familiya', '')}"
            user_id_num = u.get('id_num', '?')
        else:
            user_name = user.first_name
            user_id_num = "?"
    except Exception:
        user_name = user.first_name
        user_id_num = "?"

    # Adminga xabar yuborish
    admin_text = (
        "💳 <b>Yangi to'lov so'rovi</b>\n\n"
        f"👤 <b>Foydalanuvchi:</b> {user_name}\n"
        f"🆔 <b>ID:</b> <code>{user_id_num}</code>\n"
        f"🔗 <b>Telegram:</b> @{user.username or 'yoq'}\n\n"
        "📸 Chek rasmini tekshiring.\n\n"
        "Tasdiqlash uchun:\n"
        f"/approve_{user.id}\n\n"
        "Bekor qilish uchun:\n"
        f"/reject_{user.id}"
    )

    try:
        # Adminga chek rasmni yuborish
        if not ADMIN_TELEGRAM_ID:
            raise Exception("ADMIN_TELEGRAM_ID sozlanmagan")
        await context.bot.send_photo(
            chat_id=ADMIN_TELEGRAM_ID,
            photo=photo.file_id,
            caption=admin_text,
            parse_mode="HTML"
        )

        # Foydalanuvchiga xabar
        await update.message.reply_text(
            "✅ <b>Chek qabul qilindi!</b>\n\n"
            "📸 Chekingiz adminga yuborildi.\n"
            "⏳ Admin tasdiqlashini kuting.\n\n"
            "Tasdiqlangandan keyin sizga xabar beriladi.",
            parse_mode="HTML",
            reply_markup=payment_keyboard()
        )
    except Exception as e:
        logger.error(f"Adminga xabar yuborishda xatolik: {e}")
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.\n\n"
            "Yoki admin bilan bog'laning: @yahyobeknormurodov",
            parse_mode="HTML",
            reply_markup=payment_keyboard()
        )

    context.user_data.pop("payment_step", None)
    return ConversationHandler.END


async def approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin to'lovni tasdiqlash"""
    if not ADMIN_TELEGRAM_ID or update.effective_user.id != int(ADMIN_TELEGRAM_ID):
        await update.message.reply_text("⛔ Sizda admin huquqi yo'q.")
        return

    # Extract user ID from command
    text = update.message.text
    try:
        user_id = int(text.split("_")[1])
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Noto'g'ri format. /approve_USER_ID")
        return

    try:
        # Foydalanuvchi ma'lumotlarini olish
        user_data = sb.table("ispu_users").select("*").eq("telegram_id", user_id).execute()
        if not user_data.data:
            await update.message.reply_text(f"❌ Foydalanuvchi topilmadi: {user_id}")
            return

        user = user_data.data[0]

        # VIP ni yoqish
        expire_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        sb.table("ispu_users").update({
            "vip_status": "vip",
            "vip_expire_date": expire_date,
            "vip_plan": "solo"
        }).eq("telegram_id", user_id).execute()

        # Foydalanuvchiga xabar yuborish
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 <b>To'lov tasdiqlandi!</b>\n\n"
                "✅ VIP status faollashtirildi!\n"
                f"📅 Tugash sanasi: {expire_date}\n\n"
                "🚀 Endi barcha imkoniyatlardan foydalanishingiz mumkin:\n"
                "• Cheksiz mock testlar\n"
                "• Cheksiz modullar\n"
                "• Barcha darslar\n"
                "• AI tahlilchi\n\n"
                "🌐 ispu.uz ga kiring va boshlang!"
            ),
            parse_mode="HTML"
        )
        await update.message.reply_text(f"✅ To'lov tasdiqlandi! Foydalanuvchi: {user.get('ism', user_id)}")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")


async def reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin to'lovni rad etish"""
    if not ADMIN_TELEGRAM_ID or update.effective_user.id != int(ADMIN_TELEGRAM_ID):
        await update.message.reply_text("⛔ Sizda admin huquqi yo'q.")
        return

    text = update.message.text
    try:
        user_id = int(text.split("_")[1])
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Noto'g'ri format. /reject_USER_ID")
        return

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ <b>To'lov rad etildi</b>\n\n"
                "Chekingiz tasdiqlanmadi.\n"
                "Iltimos, qaytadan to'lov qiling.\n\n"
                "Savolingiz bo'lsa: @yahyobeknormurodov"
            ),
            parse_mode="HTML"
        )
        await update.message.reply_text(f"❌ To'lov rad etildi. Foydalanuvchi: {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")
