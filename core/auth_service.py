import re
from database.supabase_client import db, TABLE_USERS, TABLE_DEVICES, log_nac_event


def normalize_mac(mac: str) -> str:
    hex_only = re.sub(r"[^0-9a-fA-F]", "", mac or "").lower()
    if len(hex_only) != 12:
        return (mac or "").strip().lower()
    return ":".join(hex_only[i:i + 2] for i in range(0, 12, 2))


class AuthService:
    """802.1X PEAP ve MAC Binding işlemlerini yürüten servis."""

    @staticmethod
    def authenticate_peap(username: str, password_hash: str, mac_address: str) -> dict:
        mac_address = normalize_mac(mac_address)

        # 1. Kullanıcı kontrolü
        user_res = db.table(TABLE_USERS).select("*").eq("username", username).execute()

        if not user_res.data:
            log_nac_event(mac_address, "AUTH_FAIL", f"Kullanıcı bulunamadı: {username}")
            return {"status": False, "reason": "Kullanıcı bulunamadı"}

        user_data = user_res.data[0]
        user_id = user_data["id"]

        # 2. Şifre kontrolü
        if user_data.get("password_hash") != password_hash:
            log_nac_event(mac_address, "AUTH_FAIL", f"Hatalı şifre: {username}")
            return {"status": False, "reason": "Hatalı şifre", "user_id": user_id}

        # 3. Cihaz ve MAC binding kontrolü
        device_res = db.table(TABLE_DEVICES).select("*").ilike("mac_address", mac_address).execute()

        if not device_res.data:
            log_nac_event(mac_address, "AUTH_FAIL", "Rogue cihaz (MAC kayıtlı değil)")
            return {"status": False, "reason": "Rogue cihaz", "user_id": user_id}

        device_data = device_res.data[0]

        if str(device_data.get("owner_id")) != str(user_id):
            log_nac_event(mac_address, "AUTH_FAIL", f"MAC Binding İhlali: {username}")
            return {"status": False, "reason": "MAC Binding ihlali", "user_id": user_id}

        log_nac_event(mac_address, "AUTH_SUCCESS", f"Başarılı giriş: {username}")
        return {"status": True, "device_data": device_data, "user_data": user_data}