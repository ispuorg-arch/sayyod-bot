"""
Barcha userlarni tozalash — Supabase database
Faqat bir marta ishga tushiring!
"""
from supabase import create_client

SUPABASE_URL = "https://jjqydduhfhosiedrdxgs.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqcXlkZHVoZmhvc2llZHJkeGdzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDgwODQ5OSwiZXhwIjoyMDk2Mzg0NDk5fQ.ufyYpaaK8y5lx_FD2ubTYio61ApTcNgFPyJCgdCuh1k"

sb = create_client(SUPABASE_URL, SERVICE_KEY)

print("[CLEANUP] Barcha userlarni tozalash boshlandi...")

# 1. user_profiles (adminlardan tashqari)
try:
    sb.table("user_profiles").delete().neq("role", "admin").execute()
    print("[OK] user_profiles tozalandi (adminlar saqlandi)")
except Exception as e:
    print("[WARN] user_profiles:", e)

# 2. ispu_users (adminlardan tashqari)
try:
    sb.table("ispu_users").delete().eq("role", "user").execute()
    print("[OK] ispu_users tozalandi (adminlar saqlandi)")
except Exception as e:
    print("[WARN] ispu_users:", e)

print("\n[DONE] Tozalash tugadi!")
