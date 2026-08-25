from telegram import Update
from telegram.ext import ContextTypes
from config import ISPU_INFO, ISPU_ABOUT, VIP_FREE_UNTIL
from keyboards import main_keyboard, registered_keyboard, back_keyboard, pro_tariff_keyboard, admin_keyboard
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

sb = create_client(SUPABASE_URL, SUPABASE_KEY)
USERS_TABLE = "ispu_users"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("registration"):
        context.user_data.clear()

    telegram_id = update.effective_user.id

    # Foydalanuvchi ro'yxatdan o'tganmi tekshirish
    try:
        result = sb.table(USERS_TABLE).select("*").eq("telegram_id", telegram_id).execute()
        if result.data:
            user = result.data[0]
            # VIP holatini tekshirish
            vip_status = user.get("vip_status", "free")
            name = user.get("ism", "Foydalanuvchi")
            
            if vip_status == "vip":
                status_text = "💎 VIP a'zo"
            else:
                status_text = f"🆓 Bepul (1 oktyabrgacha bepul)"
            
            welcome_text = (
                f"Salom {name}! 👋\n\n"
                f"Men SAYYOD botman — ISPU SAT rasmiy yordamchisi.\n\n"
                f"📊 <b>Holatingiz:</b> {status_text}\n\n"
                f"🎓 <b>ISPU — International SAT Platform Uzbekistan</b>\n\n"
                f"📝 <b>Ro'yxatdan o'tish</b> — ISPU platformasiga ro'yxatdan o'tish\n"
                f"💬 <b>AI Yordamchi</b> — SAT va ISPU haqida savol-javob\n"
                f"ℹ️ <b>ISPU haqida</b> — Platforma haqida ma'lumot\n"
                f"📞 <b>Bog'lanish</b> — Admin bilan bog'lanish\n\n"
                f"🌐 Veb-sayt: ispu.uz\n"
                f"💬 Telegram guruh: @SATeducational\n\n"
                f"Ro'yxatdan o'tish uchun tugmani bosing! 👇"
            )
            await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=registered_keyboard())
            return
    except Exception:
        pass

    # Deep link tekshirish
    if context.args:
        arg = context.args[0]

        if arg == "login":
            from keyboards import phone_keyboard
            await update.message.reply_text(
                "🔐 <b>ISPU SAT ga kirish</b>\n\n"
                "Telefon raqamingizni tasdiqlash uchun kontakt yuboring.",
                parse_mode="HTML",
                reply_markup=phone_keyboard()
            )
            context.user_data["login_mode"] = True
            return "PHONE"

    # Oddiy /start
    user = update.effective_user
    welcome_text = (
        f"Salom {user.first_name}! 👋\n\n"
        f"Men SAYYOD botman — ISPU SAT rasmiy yordamchisi.\n\n"
        f"🎓 <b>ISPU — International SAT Platform Uzbekistan</b>\n\n"
        f"📝 <b>Ro'yxatdan o'tish</b> — ISPU platformasiga ro'yxatdan o'tish\n"
        f"💬 <b>AI Yordamchi</b> — SAT va ISPU haqida savol-javob\n"
        f"ℹ️ <b>ISPU haqida</b> — Platforma haqida ma'lumot\n"
        f"📞 <b>Bog'lanish</b> — Admin bilan bog'lanish\n\n"
        f"🌐 Veb-sayt: ispu.uz\n"
        f"💬 Telegram guruh: @SATeducational\n\n"
        f"⚠️ <b>Diqqat!</b> Sayt 1 oktyabrgacha bepul!\n\n"
        f"Ro'yxatdan o'tish uchun tugmani bosing! 👇"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=main_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 <b>Yordam</b>\n\n"
        "Buyruqlar:\n"
        "/start — Botni qayta ishga tushirish\n"
        "/help — Yordam olish\n"
        "/register — Ro'yxatdan o'tish\n"
        "/profile — Mening profilim\n"
        "/status — VIP holatini tekshirish\n\n"
        "Funksiyalar:\n"
        "📝 Ro'yxatdan o'tish\n"
        "👤 Mening profilim\n"
        "💎 VIP obuna\n"
        "💬 AI Yordamchi\n"
        "ℹ️ ISPU haqida\n"
        "📞 Bog'lanish\n\n"
        "Savol: @yahyobeknormurodov"
    )
    await update.message.reply_text(help_text, parse_mode="HTML", reply_markup=main_keyboard())


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mening profilim — Supabase dan ma'lumot olish"""
    telegram_id = update.effective_user.id
    
    try:
        result = sb.table(USERS_TABLE).select("*").eq("telegram_id", telegram_id).execute()
        if result.data:
            user = result.data[0]
            vip_status = user.get("vip_status", "free")
            vip_expire = user.get("vip_expire_date", "")
            vip_plan = user.get("vip_plan", "")
            
            if vip_status == "vip":
                vip_text = f"💎 VIP a'zo\n📋 Tarif: {vip_plan}\n📅 Tugash: {vip_expire}"
            else:
                vip_text = f"🆓 Bepul (1 oktyabrgacha bepul)"
            
            profile_text = (
                "👤 <b>Mening profilim</b>\n\n"
                f"👤 <b>Ism:</b> {user.get('ism', '—')} {user.get('familiya', '')}\n"
                f"📱 <b>Telefon:</b> {user.get('phone', '—')}\n"
                f"🔐 <b>Login:</b> {user.get('login', '—')}\n"
                f"📊 <b>Holat:</b> {vip_text}\n\n"
                f"🌐 <a href='https://ispu.uz'>Saytga kirish</a>"
            )
            await update.message.reply_text(profile_text, parse_mode="HTML", reply_markup=registered_keyboard())
        else:
            await update.message.reply_text(
                "⚠️ Profilingiz topilmadi. Qaytadan ro'yxatdan o'ting.",
                parse_mode="HTML",
                reply_markup=main_keyboard()
            )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Xatolik: {e}",
            parse_mode="HTML",
            reply_markup=registered_keyboard()
        )


async def user_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """VIP holatini tekshirish"""
    telegram_id = update.effective_user.id
    
    try:
        result = sb.table(USERS_TABLE).select("*").eq("telegram_id", telegram_id).execute()
        if result.data:
            user = result.data[0]
            vip_status = user.get("vip_status", "free")
            vip_expire = user.get("vip_expire_date", "")
            vip_plan = user.get("vip_plan", "")
            
            if vip_status == "vip":
                status_text = (
                    "💎 <b>VIP status: Faol</b>\n\n"
                    f"📋 <b>Tarif:</b> {vip_plan}\n"
                    f"📅 <b>Tugash sanasi:</b> {vip_expire}\n\n"
                    "✅ Barcha imkoniyatlar ochiq!\n"
                    "📚 Cheksiz darslar\n"
                    "🧪 Cheksiz mock testlar\n"
                    "🤖 AI tahlilchi"
                )
            else:
                status_text = (
                    "🆓 <b>Bepul rejada</b>\n\n"
                    "⚠️ Hozircha sayt 1 oktyabrgacha bepul!\n\n"
                    "📊 <b>Sizning imkoniyatlaringiz:</b>\n"
                    "• 3 ta mock test\n"
                    "• 12 ta modul\n"
                    "• 1 ta dars\n"
                    "• AI yo'q\n\n"
                    "💎 <b>VIP obuna bilan:</b>\n"
                    "• Cheksiz mock testlar\n"
                    "• Cheksiz modullar\n"
                    "• Barcha darslar\n"
                    "• AI tahlilchi\n\n"
                    "💳 VIP obuna uchun: /tolov"
                )
            
            await update.message.reply_text(status_text, parse_mode="HTML", reply_markup=registered_keyboard())
        else:
            await update.message.reply_text(
                "⚠️ Profilingiz topilmadi.",
                parse_mode="HTML",
                reply_markup=main_keyboard()
            )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Xatolik: {e}",
            parse_mode="HTML",
            reply_markup=registered_keyboard()
        )


async def pro_tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tariff_text = (
        "💎 <b>VIP obuna</b>\n\n"
        "ISPU SAT platformasining premium imkoniyatlarini oching!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🚀 <b>Solo — {VIP_FREE_UNTIL} gacha bepul!</b>\n"
        "• 1 kishi uchun\n"
        "• 20,000 so'm/oy\n"
        "• Cheksiz mock testlar\n"
        "• AI tahlilchi\n"
        "• Barcha darslar va modullar\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🚀 <b>Pro — {VIP_FREE_UNTIL} gacha bepul!</b>\n"
        "• 3 kishi uchun\n"
        "• 45,000 so'm/oy (25% tejamkorlik)\n"
        "• Hamma narsa ochiq\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚠️ <b>Diqqat!</b> Hozircha sayt {VIP_FREE_UNTIL} gacha bepul!\n\n"
        "💳 To'lov uchun: /tolov\n"
        "Veb-sayt: ispu.uz"
    )
    await update.message.reply_text(tariff_text, parse_mode="HTML", reply_markup=pro_tariff_keyboard())


async def free_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🎁 <b>Bepul sinov</b>\n\n"
        f"⚠️ <b>Diqqat!</b> Hozircha sayt {VIP_FREE_UNTIL} gacha bepul!\n\n"
        "✅ Barcha mock testlar\n"
        "✅ AI tahlilchi\n"
        "✅ Barcha darslar\n\n"
        "🌐 ispu.uz ga kiring va boshlang!",
        parse_mode="HTML",
        reply_markup=registered_keyboard()
    )


async def lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 <b>Darslar</b>\n\n"
        "ISPU SAT darslarini ko'rish uchun veb-saytga kiring:\n\n"
        "🌐 <a href='https://ispu.uz'>ispu.uz</a>\n\n"
        "📖 Reading & Writing\n"
        "🔢 Mathematics\n"
        "📝 Mock Testlar\n"
        "🤖 AI Tahlilchi\n\n"
        "⚠️ <b>Diqqat!</b> Hozircha sayt 1 oktyabrgacha bepul!\n\n"
        "💎 VIP obuna bilan barcha darslar ochiladi!",
        parse_mode="HTML",
        reply_markup=registered_keyboard()
    )


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_text = (
        "📞 <b>Bog'lanish</b>\n\n"
        f"📱 Telefon: <code>{ISPU_INFO['phone']}</code>\n"
        f"💬 Telegram: {ISPU_INFO['telegram']}\n"
        f"🌐 Veb-sayt: {ISPU_INFO['website']}\n"
        f"📍 Manzil: {ISPU_INFO['address']}\n\n"
        "Savolaringiz bo'lsa, bemalol yozing!"
    )
    await update.message.reply_text(contact_text, parse_mode="HTML", reply_markup=registered_keyboard())


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await start(update, context)


async def ispu_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ISPU_ABOUT, parse_mode="HTML", reply_markup=registered_keyboard())


async def coming_soon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ishlamaydigan tugmalar uchun 'tez orada' javobi"""
    await update.message.reply_text(
        "⏳ <b>Tez orada!</b>\n\n"
        "Bu funksiya hozircha tayyorlanmoqda.\n"
        "Hozircha saytdan foydalaning: <a href='https://ispu.uz'>ispu.uz</a>\n\n"
        "⚠️ <b>Diqqat!</b> Sayt 1 oktyabrgacha bepul!",
        parse_mode="HTML",
        reply_markup=registered_keyboard()
    )


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin paneli"""
    user_id = update.effective_user.id
    
    # Admin ekanligini tekshirish
    try:
        result = sb.table(USERS_TABLE).select("role").eq("telegram_id", user_id).execute()
        if result.data and result.data[0].get("role") == "admin":
            admin_text = (
                "🔧 <b>Admin paneli</b>\n\n"
                "Boshqaruv paneliga xush kelibsiz!\n\n"
                "👥 Foydalanuvchilar — barcha foydalanuvchilar ro'yxati\n"
                "📊 Statistika — platforma statistikasi\n"
                "📢 Xabar yuborish — barchaga xabar yuborish\n"
                "💳 To'lovlar — to'lov so'rovlari"
            )
            await update.message.reply_text(admin_text, parse_mode="HTML", reply_markup=admin_keyboard())
        else:
            await update.message.reply_text(
                "⛔ Sizda admin huquqi yo'q!",
                parse_mode="HTML",
                reply_markup=registered_keyboard()
            )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Xatolik: {e}",
            parse_mode="HTML",
            reply_markup=registered_keyboard()
        )


async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin — foydalanuvchilar ro'yxati"""
    user_id = update.effective_user.id
    
    try:
        result = sb.table(USERS_TABLE).select("role").eq("telegram_id", user_id).execute()
        if result.data and result.data[0].get("role") == "admin":
            users_result = sb.table(USERS_TABLE).select("ism,familiya,login,vip_status,role").execute()
            if users_result.data:
                users_text = "👥 <b>Foydalanuvchilar ro'yxati:</b>\n\n"
                for i, u in enumerate(users_result.data[:20], 1):
                    name = f"{u.get('ism', '?')} {u.get('familiya', '')}"
                    vip = "💎" if u.get("vip_status") == "vip" else "🆓"
                    role = "👑" if u.get("role") == "admin" else ""
                    users_text += f"{i}. {vip} {role} {name}\n"
                
                if len(users_result.data) > 20:
                    users_text += f"\n... va {len(users_result.data) - 20} ta boshqa"
                
                await update.message.reply_text(users_text, parse_mode="HTML", reply_markup=admin_keyboard())
            else:
                await update.message.reply_text("📭 Foydalanuvchilar topilmadi", reply_markup=admin_keyboard())
        else:
            await update.message.reply_text("⛔ Sizda admin huquqi yo'q!", reply_markup=admin_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}", reply_markup=admin_keyboard())


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin — statistika"""
    user_id = update.effective_user.id
    
    try:
        result = sb.table(USERS_TABLE).select("role").eq("telegram_id", user_id).execute()
        if result.data and result.data[0].get("role") == "admin":
            # Statistika
            all_users = sb.table(USERS_TABLE).select("id").execute()
            vip_users = sb.table(USERS_TABLE).select("id").eq("vip_status", "vip").execute()
            
            total = len(all_users.data) if all_users.data else 0
            vip = len(vip_users.data) if vip_users.data else 0
            free = total - vip
            
            stats_text = (
                "📊 <b>Platforma statistikasi</b>\n\n"
                f"👥 <b>Jami foydalanuvchilar:</b> {total}\n"
                f"💎 <b>VIP a'zolar:</b> {vip}\n"
                f"🆓 <b>Bepul foydalanuvchilar:</b> {free}\n\n"
                f"📅 <b>Bepul muddat:</b> 1 oktyabr 2026 gacha"
            )
            await update.message.reply_text(stats_text, parse_mode="HTML", reply_markup=admin_keyboard())
        else:
            await update.message.reply_text("⛔ Sizda admin huquqi yo'q!", reply_markup=admin_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}", reply_markup=admin_keyboard())
