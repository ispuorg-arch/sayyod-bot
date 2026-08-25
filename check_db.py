from supabase import create_client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Mavjud foydalanuvchilarni tekshirish
result = sb.table('ispu_users').select('id,vip_status,phone,telegram_id').limit(5).execute()
print("Mavjud foydalanuvchilar:")
for u in result.data:
    print(f"  ID: {u['id']}, vip: {u.get('vip_status')}, phone: {u.get('phone')}, tg_id: {u.get('telegram_id')}")

# Columnlar mavjudligini tekshirish
print("\nJadval tuzilmasini tekshirish...")
try:
    r = sb.table('ispu_users').select('*').limit(1).execute()
    if r.data:
        print("Columnlar:", list(r.data[0].keys()))
except Exception as e:
    print(f"Xatolik: {e}")
