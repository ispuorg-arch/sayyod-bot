from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

result = sb.table('ispu_users').select('id,telegram_id,ism,familiya,login,role,vip_status').execute()

if result.data:
    print('=== USERLAR ROYXATI ===')
    print(f'Jami: {len(result.data)} ta\n')
    for i, u in enumerate(result.data, 1):
        name = f"{u.get('ism', '?')} {u.get('familiya', '')}"
        tg_id = u.get('telegram_id', 'yoq')
        role = u.get('role', '?')
        vip = u.get('vip_status', 'free')
        login = u.get('login', '?')
        print(f"{i}. {name} | TG ID: {tg_id} | Login: {login} | Role: {role} | VIP: {vip}")
else:
    print('Userlar topilmadi')
