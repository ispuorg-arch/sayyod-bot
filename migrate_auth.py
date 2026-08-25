"""
Mavjud foydalanuvchilarni Supabase Auth ga migrate qilish
Faqat bir marta ishga tushiring!
"""
from supabase import create_client

SUPABASE_URL = "https://jjqydduhfhosiedrdxgs.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqcXlkZHVoZmhvc2llZHJkeGdzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDgwODQ5OSwiZXhwIjoyMDk2Mzg0NDk5fQ.ufyYpaaK8y5lx_FD2ubTYio61ApTcNgFPyJCgdCuh1k"

sb = create_client(SUPABASE_URL, SERVICE_KEY)

print("[MIGRATE] Supabase Auth ga o'tkazish boshlandi...")

# 1. Barcha foydalanuvchilarni olish
result = sb.table("ispu_users").select("id,login,parol,ism,familiya,auth_user_id").execute()
users = result.data

print(f"[INFO] Jami foydalanuvchilar: {len(users)}")

# 2. Auth user yo'q foydalanuvchilar
migrate_needed = [u for u in users if not u.get("auth_user_id")]
print(f"[INFO] Migrate kerak: {len(migrate_needed)}")

success = 0
errors = 0

for user in migrate_needed:
    login = user["login"]
    password = user["parol"]
    user_id = user["id"]
    ism = user.get("ism", "")
    familiya = user.get("familiya", "")

    try:
        # Auth user yaratish
        synthetic_email = f"{login}@ispu.uz"

        # Parol hali plaintext bo'lsa — oddiy parol sifatida ishlatamiz
        # Agar bcrypt bo'lsa — eski parolni ishlatamiz
        if password and password.startswith("$2"):
            # Bcrypt hash — Supabase Auth ga o'tkazib bo'lmaydi
            # Yangi parol kerak yoki qo'lda boshqarish
            print(f"[SKIP] {login} — bcrypt parol, qo'lda boshqarish kerak")
            continue

        auth_result = sb.auth.admin.create_user({
            "email": synthetic_email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {
                "ism": ism,
                "familiya": familiya,
                "login": login
            }
        })

        auth_user_id = auth_result.user.id

        # ispu_users ni yangilash
        sb.table("ispu_users").update({
            "auth_user_id": auth_user_id
        }).eq("id", user_id).execute()

        print(f"[OK] {login} — Auth user yaratildi: {auth_user_id}")
        success += 1

    except Exception as e:
        error_msg = str(e).lower()
        if "already" in error_msg or "exist" in error_msg:
            print(f"[SKIP] {login} — allaqachon mavjud")
        else:
            print(f"[ERROR] {login} — {e}")
        errors += 1

print(f"\n[DONE] Muvaffaqiyatli: {success}, Xatolik: {errors}")
