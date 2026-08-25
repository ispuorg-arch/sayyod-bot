import re
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import Forbidden, BadRequest
from supabase import create_client
from config import (
    SUPABASE_URL,
    SUPABASE_KEY,
    SUPABASE_SERVICE_KEY
)
from keyboards import (
    main_keyboard,
    registered_keyboard,
    back_keyboard,
    phone_keyboard,
    confirm_keyboard
)

# Service role client
sb_service = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
# Anon client
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

USERS_TABLE = "ispu_users"


async def safe_reply(update: Update, text: str, parse_mode="HTML", reply_markup=None):
    """Xavfsiz reply — bloklangan user uchun xatolarni tutadi"""
    try:
        await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
        return True
    except Forbidden:
        return False
    except BadRequest as e:
        print(f"BadRequest: {e}")
        return False
    except Exception as e:
        print(f"Reply error: {e}")
        return False


def _is_valid_login(login: str) -> bool:
    if len(login) < 4 or len(login) > 20:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', login))


def _check_login_exists(login: str) -> bool:
    try:
        result = sb.table(USERS_TABLE).select("id").eq("login", login).execute()
        return len(result.data) > 0
    except Exception:
        return False


def _generate_id_num() -> str:
    try:
        result = sb.table(USERS_TABLE).select("id_num").order("id", desc=True).limit(1).execute()
        if result.data:
            last_num = int(result.data[0]["id_num"].replace("#", ""))
            new_num = last_num + 1
        else:
            new_num = 100001
        return f"#{new_num:06d}"
    except Exception:
        return "#100001"


def _back_confirm_kb():
    return {
        "keyboard": [
            [{"text": "✅ Davom etish"}],
            [{"text": "❌ Bekor qilish"}]
        ],
        "resize_keyboard": True
    }


# ============================================
# Cancel — istalgan paytda /cancel yoki /start
# ============================================

async def reg_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    from handlers import start as do_start
    await do_start(update, context)
    return ConversationHandler.END


# ============================================
# Registration Flow
# ============================================

async def reg_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["registration"] = True

    telegram_id = update.effective_user.id
    context.user_data["telegram_id"] = telegram_id

    # Allaqachon ro'yxatdan o'tganmi?
    try:
        existing = sb.table(USERS_TABLE).select("id,ism,familiya").eq("telegram_id", telegram_id).execute()
        if existing.data:
            user = existing.data[0]
            await safe_reply(
                update,
                "⚠️ <b>Siz allaqachon ro'yxatdan o'tgansiz!</b>\n\n"
                f"👤 <b>Ismingiz:</b> {user.get('ism', '')} {user.get('familiya', '')}\n\n"
                "📊 Profilingizni ko'rish uchun /profile buyrug'ini yozing.\n"
                "🌐 Saytga kirish uchun: ispu.uz",
                reply_markup=registered_keyboard()
            )
            return ConversationHandler.END
    except Exception:
        pass

    ok = await safe_reply(
        update,
        "📝 <b>Ro'yxatdan o'tish</b>\n\n"
        "ISPU SAT platformasiga ro'yxatdan o'tish uchun "
        "quyidagi ma'lumotlarni kiriting.\n\n"
        "❌ Bekor qilish uchun /cancel buyrug'ini yozing.",
        reply_markup=back_keyboard()
    )
    if not ok:
        return ConversationHandler.END

    await safe_reply(update, "1️⃣ <b>Ismingizni kiriting:</b>")
    return "FIRST_NAME"


# ─── 1. ISM ───

async def reg_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🔙 Orqaga":
        if context.user_data.get("first_name"):
            await safe_reply(
                update,
                "⚠️ <b>Diqqat!</b>\n\n"
                "Oldingi ma'lumotlar tozalanadi.\n\n"
                "Davom etasizmi?",
                reply_markup=_back_confirm_kb()
            )
            context.user_data["_back_to"] = "FIRST_NAME"
            return "BACK_CONFIRM"
        else:
            context.user_data.clear()
            from handlers import start as do_start
            await do_start(update, context)
            return ConversationHandler.END

    if len(text) < 2:
        await safe_reply(update, "❌ Ism juda qisqa. Kamida 2 ta belgi kiriting.", reply_markup=back_keyboard())
        return "FIRST_NAME"

    context.user_data["first_name"] = text
    await safe_reply(
        update,
        f"✅ Ism: <b>{text}</b>\n\n2️⃣ <b>Familiyangizni kiriting:</b>",
        reply_markup=back_keyboard()
    )
    return "LAST_NAME"


# ─── 2. FAMILIYA ───

async def reg_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🔙 Orqaga":
        if context.user_data.get("last_name"):
            await safe_reply(
                update,
                "⚠️ <b>Diqqat!</b>\n\n"
                "Oldingi ma'lumotlar tozalanadi.\n\n"
                "Davom etasizmi?",
                reply_markup=_back_confirm_kb()
            )
            context.user_data["_back_to"] = "LAST_NAME"
            return "BACK_CONFIRM"
        else:
            await safe_reply(update, "1️⃣ <b>Ismingizni kiriting:</b>", reply_markup=back_keyboard())
            return "FIRST_NAME"

    context.user_data["last_name"] = text
    first_name = context.user_data.get("first_name", "")
    await safe_reply(
        update,
        f"✅ Ism: <b>{first_name}</b>\n"
        f"✅ Familiya: <b>{text}</b>\n\n"
        "3️⃣ <b>Telefon raqamingizni kiriting:</b>\n"
        "(+998 XX XXX XX XX formatida)",
        reply_markup=phone_keyboard()
    )
    return "PHONE"


# ─── 3. TELEFON ───

async def reg_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone
        context.user_data["phone"] = phone
        first_name = context.user_data.get("first_name", "")
        last_name = context.user_data.get("last_name", "")
        await safe_reply(
            update,
            f"✅ Ism: <b>{first_name}</b>\n"
            f"✅ Familiya: <b>{last_name}</b>\n"
            f"✅ Telefon: <code>{phone}</code>\n\n"
            "4️⃣ <b>Login kiriting:</b>\n"
            "(Kamida 4 ta belgi, faqat harflar va raqamlar)",
            reply_markup=back_keyboard()
        )
        return "LOGIN"

    text = update.message.text

    if text == "🔙 Orqaga":
        if context.user_data.get("phone"):
            await safe_reply(
                update,
                "⚠️ <b>Diqqat!</b>\n\n"
                "Oldingi ma'lumotlar tozalanadi.\n\n"
                "Davom etasizmi?",
                reply_markup=_back_confirm_kb()
            )
            context.user_data["_back_to"] = "PHONE"
            return "BACK_CONFIRM"
        else:
            await safe_reply(update, "2️⃣ <b>Familiyangizni kiriting:</b>", reply_markup=back_keyboard())
            return "LAST_NAME"

    phone = text.strip()
    if not phone.startswith("+998"):
        await safe_reply(update, "❌ Noto'g'ri format. +998 XX XXX XX XX formatida kiriting.", reply_markup=phone_keyboard())
        return "PHONE"
    if len(phone) != 13:
        await safe_reply(update, "❌ Telefon raqami 13 ta belgi bo'lishi kerak (+998 bilan).", reply_markup=phone_keyboard())
        return "PHONE"

    context.user_data["phone"] = phone
    first_name = context.user_data.get("first_name", "")
    last_name = context.user_data.get("last_name", "")
    await safe_reply(
        update,
        f"✅ Ism: <b>{first_name}</b>\n"
        f"✅ Familiya: <b>{last_name}</b>\n"
        f"✅ Telefon: <code>{phone}</code>\n\n"
        "4️⃣ <b>Login kiriting:</b>\n"
        "(Kamida 4 ta belgi, faqat harflar va raqamlar)",
        reply_markup=back_keyboard()
    )
    return "LOGIN"


# ─── 4. LOGIN ───

async def reg_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🔙 Orqaga":
        if context.user_data.get("login"):
            await safe_reply(
                update,
                "⚠️ <b>Diqqat!</b>\n\n"
                "Oldingi ma'lumotlar tozalanadi.\n\n"
                "Davom etasizmi?",
                reply_markup=_back_confirm_kb()
            )
            context.user_data["_back_to"] = "LOGIN"
            return "BACK_CONFIRM"
        else:
            await safe_reply(
                update,
                "3️⃣ <b>Telefon raqamingizni kiriting:</b>\n"
                "(+998 XX XXX XX XX formatida)",
                reply_markup=phone_keyboard()
            )
            return "PHONE"

    if not _is_valid_login(text):
        await safe_reply(update, "❌ Login noto'g'ri. Kamida 4 ta belgi, faqat harflar va raqamlar.", reply_markup=back_keyboard())
        return "LOGIN"

    if _check_login_exists(text):
        await safe_reply(update, "❌ Bu login allaqachon mavjud. Boshqa login kiriting.", reply_markup=back_keyboard())
        return "LOGIN"

    context.user_data["login"] = text
    first_name = context.user_data.get("first_name", "")
    last_name = context.user_data.get("last_name", "")
    phone = context.user_data.get("phone", "")
    await safe_reply(
        update,
        f"✅ Ism: <b>{first_name}</b>\n"
        f"✅ Familiya: <b>{last_name}</b>\n"
        f"✅ Telefon: <code>{phone}</code>\n"
        f"✅ Login: <b>{text}</b>\n\n"
        "5️⃣ <b>Parol kiriting:</b>\n"
        "(Kamida 6 ta belgi)",
        reply_markup=back_keyboard()
    )
    return "PASSWORD"


# ─── 5. PAROL ───

async def reg_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🔙 Orqaga":
        await safe_reply(
            update,
            "4️⃣ <b>Login kiriting:</b>\n"
            "(Kamida 4 ta belgi, faqat harflar va raqamlar)",
            reply_markup=back_keyboard()
        )
        return "LOGIN"

    if len(text) < 6:
        await safe_reply(update, "❌ Parol juda qisqa. Kamida 6 ta belgi kiriting.", reply_markup=back_keyboard())
        return "PASSWORD"

    context.user_data["password"] = text
    await safe_reply(
        update,
        "6️⃣ <b>Parolni tasdiqlang:</b>",
        reply_markup=back_keyboard()
    )
    return "PASSWORD_CONFIRM"


# ─── 6. PAROL TASDIQLASH ───

async def reg_password_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🔙 Orqaga":
        await safe_reply(
            update,
            "5️⃣ <b>Parol kiriting:</b>\n"
            "(Kamida 6 ta belgi)",
            reply_markup=back_keyboard()
        )
        return "PASSWORD"

    password = context.user_data.get("password", "")
    if text != password:
        await safe_reply(update, "❌ Parollar mos emas. Qaytadan kiriting.", reply_markup=back_keyboard())
        return "PASSWORD_CONFIRM"

    first_name = context.user_data.get("first_name", "")
    last_name = context.user_data.get("last_name", "")
    phone = context.user_data.get("phone", "")
    login = context.user_data.get("login", "")
    await safe_reply(
        update,
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 <b>Ma'lumotlaringiz:</b>\n\n"
        f"👤 Ism: <b>{first_name}</b>\n"
        f"👤 Familiya: <b>{last_name}</b>\n"
        f"📱 Telefon: <code>{phone}</code>\n"
        f"🔐 Login: <b>{login}</b>\n"
        f"🔑 Parol: <code>{'•' * len(text)}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✅ Barcha ma'lumotlar to'g'ri?",
        reply_markup=confirm_keyboard()
    )
    return "CONFIRM"


# ─── 7. TASDIQLASH ───

async def reg_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "❌ Bekor qilish":
        context.user_data.clear()
        from handlers import start as do_start
        await do_start(update, context)
        return ConversationHandler.END

    if text == "✅ Tasdiqlash":
        return await _create_user(update, context)

    await safe_reply(update, "❌ Tugmalardan birini bosing.", reply_markup=confirm_keyboard())
    return "CONFIRM"


# ─── BACK CONFIRM ───

async def back_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    back_to = context.user_data.get("_back_to")

    if text == "✅ Davom etish":
        context.user_data.pop("_back_to", None)

        if back_to == "FIRST_NAME":
            await safe_reply(update, "1️⃣ <b>Ismingizni kiriting:</b>", reply_markup=back_keyboard())
            return "FIRST_NAME"
        elif back_to == "LAST_NAME":
            await safe_reply(update, "2️⃣ <b>Familiyangizni kiriting:</b>", reply_markup=back_keyboard())
            return "LAST_NAME"
        elif back_to == "PHONE":
            await safe_reply(
                update,
                "3️⃣ <b>Telefon raqamingizni kiriting:</b>\n(+998 XX XXX XX XX formatida)",
                reply_markup=phone_keyboard()
            )
            return "PHONE"
        elif back_to == "LOGIN":
            await safe_reply(
                update,
                "4️⃣ <b>Login kiriting:</b>\n(Kamida 4 ta belgi, faqat harflar va raqamlar)",
                reply_markup=back_keyboard()
            )
            return "LOGIN"
        else:
            await safe_reply(update, "1️⃣ <b>Ismingizni kiriting:</b>", reply_markup=back_keyboard())
            return "FIRST_NAME"

    elif text == "❌ Bekor qilish":
        context.user_data.clear()
        await safe_reply(update, "✅ Bekor qilindi.", reply_markup=main_keyboard())
        return ConversationHandler.END

    else:
        await safe_reply(update, "Tugmalardan birini bosing.", reply_markup=_back_confirm_kb())
        return "BACK_CONFIRM"


# ============================================
# User yaratish
# ============================================

async def _create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = context.user_data["first_name"]
    last_name = context.user_data["last_name"]
    login = context.user_data["login"]
    password = context.user_data["password"]
    telegram_id = context.user_data.get("telegram_id", update.effective_user.id)
    phone = context.user_data.get("phone", "")

    await safe_reply(update, "⏳ <b>Ro'yxatdan o'tkazilmoqda...</b>")

    auth_user_id = None
    try:
        # 1. Supabase Auth user yaratish
        synthetic_email = f"{login}@ispu.uz"
        auth_result = sb_service.auth.admin.create_user({
            "email": synthetic_email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {
                "ism": first_name,
                "familiya": last_name,
                "phone": phone,
                "telegram_id": telegram_id,
                "login": login
            }
        })
        auth_user_id = auth_result.user.id

        # 2. ispu_users ga yozish
        id_num = _generate_id_num()
        result = sb.table(USERS_TABLE).insert({
            "id_num": id_num,
            "login": login,
            "parol": password,
            "ism": first_name,
            "familiya": last_name,
            "role": "user",
            "phone": phone,
            "telegram_id": telegram_id,
            "vip_status": "free",
            "auth_user_id": auth_user_id
        }).execute()

        if result.data:
            await safe_reply(
                update,
                "🎉 <b>TABRIKLAYMIZ!</b>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>Ism:</b> {first_name}\n"
                f"👤 <b>Familiya:</b> {last_name}\n"
                f"📱 <b>Telefon:</b> {phone}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🔐 <b>KIRISH MA'LUMOTLARI:</b>\n\n"
                f"📧 <b>Login:</b> <code>{login}</code>\n"
                f"🔑 <b>Parol:</b> <code>{password}</code>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🌐 <b>ispu.uz ga kiring va kirish!</b>\n\n"
                "📚 SAT tayyorgarlikni boshlang! 💪",
                reply_markup=registered_keyboard()
            )
        else:
            if auth_user_id:
                try:
                    sb_service.auth.admin.delete_user(auth_user_id)
                except Exception:
                    pass
            await safe_reply(update, "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.", reply_markup=main_keyboard())

        context.user_data.clear()
        return ConversationHandler.END

    except Exception as e:
        if auth_user_id:
            try:
                sb_service.auth.admin.delete_user(auth_user_id)
            except Exception:
                pass

        error_msg = str(e).lower()
        print(f"REGISTRATION ERROR: {e}")

        if "already" in error_msg or "duplicate" in error_msg or "unique" in error_msg:
            await safe_reply(
                update,
                "⚠️ <b>Uzrimiz!</b>\n\nBu hisob allaqachon mavjud.\n\n"
                "📞 Admin: <b>@yahyobeknormurodov</b>",
                reply_markup=main_keyboard()
            )
        else:
            await safe_reply(
                update,
                "❌ <b>Xatolik!</b>\n\n"
                "Qaytadan urinib ko'ring yoki admin bilan bog'laning.\n\n"
                "📞 <b>@yahyobeknormurodov</b>",
                reply_markup=main_keyboard()
            )

        context.user_data.clear()
        return ConversationHandler.END
