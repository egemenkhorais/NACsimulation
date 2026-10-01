from supabase import create_client, Client
from config.settings import SUPABASE_URL, SUPABASE_KEY

# Supabase istemcisini başlat
db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Tablo sabitleri (Büyük harf formatına göre)
TABLE_USERS = "USERS"
TABLE_DEVICES = "DEVICES"
TABLE_LOGS = "LOGS"

def get_device_by_mac(mac_address: str) -> dict:
    """Belirtilen MAC adresine sahip cihazı DEVICES tablosundan getirir."""
    response = db.table(TABLE_DEVICES).select("*").eq("mac_address", mac_address).execute()
    return response.data[0] if response.data else None

def log_nac_event(mac_address: str, event_type: str, reason: str = ""):
    """Sistem olaylarını LOGS tablosuna yazar."""
    payload = {
        "mac_address": mac_address,
        "event_type": event_type,
        "reason": reason
    }
    db.table(TABLE_LOGS).insert(payload).execute()