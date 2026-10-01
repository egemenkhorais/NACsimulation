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


def isolate_user_devices(username: str, mac: str, reason: str):
    """Kullanıcıyı username ile bulur, cihazlarını VLAN 99'a alır (zaten 99 ise dokunmaz)."""
    # 1. Kullanıcıyı bul
    user_res = db.table(TABLE_USERS).select("id").eq("username", username).execute()
    print("USER LOOKUP:", user_res.data)
    if not user_res.data:
        print(f"Kullanıcı yok, değiştirilecek bir şey yok: {username}")
        return

    user_id = user_res.data[0]["id"]

    # 2. Kullanıcının cihazlarını çek
    devices = (
        db.table(TABLE_DEVICES)
        .select("id, mac_address, assigned_vlan")
        .eq("owner_id", user_id)
        .execute()
    )
    print("USER DEVICES BEFORE:", devices.data)

    if not devices.data:
        print(f"{username} kullanıcısının devices tablosunda cihazı yok (owner_id eşleşmiyor olabilir)")
        return

    # 3. VLAN'ı 99 olmayanları 99 yap
    for d in devices.data:
        if d.get("assigned_vlan") == ISOLATION_VLAN:
            continue
        res = (
            db.table(TABLE_DEVICES)
            .update({"assigned_vlan": ISOLATION_VLAN})
            .eq("id", d["id"])
            .execute()
        )
        print(f"UPDATE device {d['id']}:", res.data)  # [] ise RLS engelliyor

    # 4. Gerçekten değişti mi, geri okuyup doğrula
    check = (
        db.table(TABLE_DEVICES)
        .select("id, mac_address, assigned_vlan")
        .eq("owner_id", user_id)
        .execute()
    )
    print("USER DEVICES AFTER:", check.data)

    log_nac_event(mac, "AUTH_FAIL_ISOLATED", f"{username} -> VLAN 99. Sebep: {reason}")


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
            isolate_user_devices(request.username, mac, auth_result.get("reason"))
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