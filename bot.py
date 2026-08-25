import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)
from telegram.error import Forbidden, BadRequest, TimedOut, NetworkError
from config import BOT_TOKEN
from handlers import (
    start,
    help_command,
    ispu_info,
    profile,
    pro_tariffs,
    free_trial,
    lessons,
    contact,
    back_to_main,
    user_status,
    coming_soon,
    admin_panel,
    admin_users,
    admin_stats
)
from registration import (
    reg_start,
    reg_first_name,
    reg_last_name,
    reg_phone,
    reg_login,
    reg_password,
    reg_password_confirm,
    reg_confirm,
    back_confirm,
    reg_cancel
)
from ai_chat import ai_chat
from payment import (
    payment_start,
    payment_made,
    receive_receipt,
    approve_payment,
    reject_payment,
    WAITING_RECEIPT
)

# Logging sozlash
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ============================================
# Global Error Handler
# ============================================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Barcha xatolarni tutadi — bot crash qilmasligi uchun"""
    error = context.error

    if isinstance(error, Forbidden):
        # User botni bloklagan yoki chatni tark etgan
        logger.warning(f"Bot bloklangan yoki chat tark etilgan: {error}")
        # ConversationHandler ni tozalash
        if update and hasattr(update, 'message') and update.message:
            chat_id = update.message.chat_id
            context.user_data.clear()
            # ConversationHandler state ni tozalash
            return ConversationHandler.END
        return

    elif isinstance(error, BadRequest):
        logger.warning(f"BadRequest xatolik: {error}")
        # "Message to edit not found" kabi xatolarni e'tiborsiz qoldirish
        return

    elif isinstance(error, TimedOut):
        logger.warning(f"Timeout xatolik: {error}")
        return

    elif isinstance(error, NetworkError):
        logger.error(f"Network xatolik: {error}")
        return

    else:
        logger.error(f"Kutilmagan xatolik: {error}", exc_info=True)


def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN sozlanmagan! .env faylni tekshiring.")
        return
    app = Application.builder().token(BOT_TOKEN).build()

    # Global error handler qo'shish
    app.add_error_handler(error_handler)

    # ==========================================
    # ConversationHandler — Ro'yxatdan o'tish
    # ==========================================

    # Ro'yxatdan o'tish tugmalaridan tashqari boshqa tugmalar — ConversationHandler tutmasin
    _NON_REG = (
        "^("
        "📝 Ro'yxatdan o'tish|💬 AI Yordamchi|ℹ️ ISPU haqida|"
        "📞 Bog'lanish|👤 Mening profilim|📊 Holatim|💎 VIP obuna|📚 Darslar|"
        "👥 Foydalanuvchilar|📊 Statistika|📢 Xabar yuborish|💳 To'lovlar|"
        "💳 To'lov|💳 To'ladim|💎 Solo|💎 Pro|🎁 Bepul sinov"
        ")$"
    )
    # Faqat oddiy matn (tugmalar emas) — ro'yxatdan o'tish uchun
    REG_TEXT = filters.TEXT & ~filters.COMMAND & ~filters.Regex(_NON_REG)

    # Har qanday holatda conversationni tugatish va /start ni qayta ishga tushirish
    async def _exit_and_restart(update, context):
        context.user_data.clear()
        await start(update, context)
        return ConversationHandler.END

    # Barcha menyu tugmalari — istalgan state'da conversationni tugatadi
    _MENU_EXIT = MessageHandler(filters.Regex(_NON_REG), _exit_and_restart)

    reg_conv = ConversationHandler(
        entry_points=[
            CommandHandler("register", reg_start),
            CommandHandler("start", _exit_and_restart),
            MessageHandler(filters.Regex("^📝 Ro'yxatdan o'tish$"), reg_start),
        ],
        states={
            "FIRST_NAME": [
                MessageHandler(REG_TEXT, reg_first_name),
                _MENU_EXIT,
            ],
            "LAST_NAME": [
                MessageHandler(REG_TEXT, reg_last_name),
                _MENU_EXIT,
            ],
            "PHONE": [
                MessageHandler(filters.CONTACT, reg_phone),
                MessageHandler(REG_TEXT, reg_phone),
                _MENU_EXIT,
            ],
            "LOGIN": [
                MessageHandler(REG_TEXT, reg_login),
                _MENU_EXIT,
            ],
            "PASSWORD": [
                MessageHandler(REG_TEXT, reg_password),
                _MENU_EXIT,
            ],
            "PASSWORD_CONFIRM": [
                MessageHandler(REG_TEXT, reg_password_confirm),
                _MENU_EXIT,
            ],
            "CONFIRM": [
                MessageHandler(filters.Regex("^✅ Tasdiqlash$"), reg_confirm),
                MessageHandler(filters.Regex("^❌ Bekor qilish$"), reg_confirm),
                _MENU_EXIT,
            ],
            "BACK_CONFIRM": [
                MessageHandler(filters.Regex("^✅ Davom etish$"), back_confirm),
                MessageHandler(filters.Regex("^❌ Bekor qilish$"), back_confirm),
                _MENU_EXIT,
            ]
        },
        fallbacks=[
            CommandHandler("cancel", reg_cancel),
            CommandHandler("start", _exit_and_restart),
            _MENU_EXIT,
        ],
        allow_reentry=True
    )

    # ==========================================
    # ConversationHandler — To'lov
    # ==========================================
    payment_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💳 To'ladim$"), payment_made)
        ],
        states={
            WAITING_RECEIPT: [
                MessageHandler(filters.Regex("^🔙 Orqaga$"), back_to_main),
                MessageHandler(filters.PHOTO, receive_receipt)
            ]
        },
        fallbacks=[
            MessageHandler(filters.Regex("^🔙 Orqaga$"), back_to_main)
        ]
    )

    # Handlerlarni qo'shish (muhim: reg_conv birinchi bo'lishi kerak!)
    app.add_handler(reg_conv)
    app.add_handler(payment_conv)
    app.add_handler(CommandHandler("help", help_command))

    # Buyruqlar
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("status", user_status))
    app.add_handler(CommandHandler("tolov", payment_start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("users", admin_users))
    app.add_handler(CommandHandler("stats", admin_stats))

    # Oddiy handlerlar
    app.add_handler(MessageHandler(filters.Regex("^🔙 Orqaga$"), back_to_main))
    app.add_handler(MessageHandler(filters.Regex("^👤 Mening profilim$"), profile))
    app.add_handler(MessageHandler(filters.Regex("^📊 Holatim$"), user_status))
    app.add_handler(MessageHandler(filters.Regex("^💎 VIP obuna$"), pro_tariffs))
    app.add_handler(MessageHandler(filters.Regex("^📚 Darslar$"), coming_soon))
    app.add_handler(MessageHandler(filters.Regex("^📞 Bog'lanish$"), contact))
    app.add_handler(MessageHandler(filters.Regex("^ℹ️ ISPU haqida$"), ispu_info))
    app.add_handler(MessageHandler(filters.Regex("^🎁 Bepul sinov$"), free_trial))
    app.add_handler(MessageHandler(filters.Regex("^💎 Solo"), pro_tariffs))
    app.add_handler(MessageHandler(filters.Regex("^💎 Pro"), pro_tariffs))

    # Admin handlerlari
    app.add_handler(MessageHandler(filters.Regex("^👥 Foydalanuvchilar$"), admin_users))
    app.add_handler(MessageHandler(filters.Regex("^📊 Statistika$"), admin_stats))
    app.add_handler(MessageHandler(filters.Regex("^📢 Xabar yuborish$"), coming_soon))
    app.add_handler(MessageHandler(filters.Regex("^💳 To'lovlar$"), coming_soon))

    # To'lov handlerlari
    app.add_handler(MessageHandler(filters.Regex("^💳 To'lov$"), payment_start))

    # Admin buyruqlari — regex bilan (approve_12345 formati uchun)
    app.add_handler(MessageHandler(filters.Regex("^/approve_\d+$"), approve_payment))
    app.add_handler(MessageHandler(filters.Regex("^/reject_\d+$"), reject_payment))

    # AI Chat — boshqa text xabarlar uchun (eng oxirida bo'lishi kerak!)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        ai_chat
    ))

    # Rasm qabul qilish — to'lov uchun
    app.add_handler(MessageHandler(
        filters.PHOTO,
        receive_receipt
    ))

    # Botni ishga tushirish
    print("SAYYOD bot ishga tushdi...")
    print("Telegram API bilan bog'lanmoqda...")
    print("Global error handler faol")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
