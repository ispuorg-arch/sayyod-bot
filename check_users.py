from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
result = sb.table('ispu_users').select('id,login,ism,familiya,telegram_id,role').execute()

for u in result.data:
    print("ID:", u.get('id'), "| Login:", u.get('login'), "| Ism:", u.get('ism'), u.get('familiya'), "| TG:", u.get('telegram_id'), "| Role:", u.get('role'))
