import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.auth_service import AuthService, normalize_mac
from core.policy_engine import PolicyEngine
from core.posture_service import PostureService
from database.supabase_client import db, TABLE_USERS, TABLE_DEVICES, log_nac_event

router = APIRouter()

ISOLATION_VLAN = 99


class AuthRequest(BaseModel):
    username: str
    password: str
    mac_address: str
    switch_port: str = "GigabitEthernet0/1"


def isolate_target_mac(mac: str, reason: str, username: str):
    print(f"\n--- SIFIR GÜVEN İZOLASYONU TETİKLENDİ ---")
    print(f"Hedef MAC: {mac} | Kullanıcı: {username} | Sebep: {reason}")

    # KESİN ÇÖZÜM: Tüm cihazları çek ve eşleşmeyi Python'da normalize ederek yap
    all_devices = db.table(TABLE_DEVICES).select("id, mac_address, assigned_vlan").execute()

    target_device = None
    for d in all_devices.data:
        # Hem gelen MAC'i hem DB'deki MAC'i aynı formata sokup kıyaslıyoruz
        if normalize_mac(d.get("mac_address")) == mac:
            target_device = d
            break

    if not target_device:
        print(f"KRİTİK HATA: {mac} adresi veritabanında BULUNAMADI!")
        # Debug için veritabanındaki mevcut MAC'leri yazdır
        db_macs = [d.get('mac_address') for d in all_devices.data]
        print(f"Mevcut Kayıtlı MAC'ler: {db_macs}")
        return

    device_id = target_device["id"]
    current_vlan = target_device.get("assigned_vlan")
    print(f"Eşleşme Başarılı -> Cihaz ID: {device_id} | Mevcut VLAN: {current_vlan}")

    if current_vlan != 99:
        try:
            print("Veritabanı güncelleniyor (VLAN -> 99)...")
            res = db.table(TABLE_DEVICES).update({
                "assigned_vlan": 99,
            }).eq("id", device_id).execute()
            print(f"GÜNCELLEME BAŞARILI: {res.data}")
            log_nac_event(mac, "AUTH_FAIL_ISOLATED", f"VLAN 99 İzolasyonu. Sebep: {reason}")
        except Exception as e:
            print(f"GÜNCELLEME ESNASINDA VERİTABANI HATASI: {str(e)}")
    else:
        print("Cihaz zaten VLAN 99 izolasyonunda, işlem atlandı.")
    print("------------------------------------------\n")

@router.post("/login")
def authenticate_endpoint(request: AuthRequest):
    mac = normalize_mac(request.mac_address)

    auth_result = AuthService.authenticate_peap(
        username=request.username,
        password_hash=request.password,
        mac_address=mac
    )

    if not auth_result.get("status"):
        try:
            # Hata yapan MAC adresini, kullanıcı adı ne olursa olsun izole et
            isolate_target_mac(mac, auth_result.get("reason"), request.username)
        except Exception:
            traceback.print_exc()

        raise HTTPException(status_code=401, detail="Kimlik doğrulama başarısız")

    # Başarılı giriş
    device = auth_result["device_data"]
    posture_status = PostureService.evaluate_health(device)

    assigned_vlan = PolicyEngine.evaluate_and_enforce(
        device_id=device["id"],
        mac_address=device["mac_address"],
        is_authenticated=True,
        posture_status=posture_status,
        is_under_attack=False
    )

    return {
        "status": "success",
        "message": f"Kullanıcı doğrulandı, cihaz VLAN {assigned_vlan} ağına atandı.",
        "vlan": assigned_vlan
    }