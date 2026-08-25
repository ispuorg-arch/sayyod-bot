-- VIP obuna uchun yangi columnlar
-- ispu_users jadvaliga qo'shish

-- VIP status (default: 'free')
ALTER TABLE ispu_users ADD COLUMN IF NOT EXISTS vip_status TEXT DEFAULT 'free';

-- VIP tugash sanasi
ALTER TABLE ispu_users ADD COLUMN IF NOT EXISTS vip_expire_date TIMESTAMP WITH TIME ZONE;

-- VIP tarif (solo yoki pro)
ALTER TABLE ispu_users ADD COLUMN IF NOT EXISTS vip_plan TEXT;

-- Telefon raqami (agar yo'q bo'lsa)
ALTER TABLE ispu_users ADD COLUMN IF NOT EXISTS phone TEXT;

-- Telegram ID (agar yo'q bo'lsa)
ALTER TABLE ispu_users ADD COLUMN IF NOT EXISTS telegram_id BIGINT;

-- Index qo'shish
CREATE INDEX IF NOT EXISTS idx_ispu_users_vip_status ON ispu_users(vip_status);
CREATE INDEX IF NOT EXISTS idx_ispu_users_telegram_id ON ispu_users(telegram_id);
