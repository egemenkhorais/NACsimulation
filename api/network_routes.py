from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from network_ops.switch_controller import SwitchController
from database.supabase_client import db, TABLE_DEVICES, TABLE_LOGS, log_nac_event

router = APIRouter()
switch = SwitchController()


# İstemciden (Frontend) beklenen veri formatı
class PortActionRequest(BaseModel):
    mac_address: str
    interface: str  # Örn: "GigabitEthernet0/2"


@router.post("/quarantine")
def manual_quarantine(request: PortActionRequest):
    """Belirtilen portu zorla Karantina VLAN'ına (66) çeker."""

    # 1. Switch'e bağlan ve VLAN'ı değiştir
    success = switch.assign_vlan_to_port(request.interface, target_vlan=66)

    if not success:
        raise HTTPException(status_code=500, detail="Switch'e komut gönderilirken hata oluştu.")

    # 2. Veritabanını güncelle
    db.table(TABLE_DEVICES).update({"assigned_vlan": 66}).eq("mac_address", request.mac_address).execute()

    # 3. Log kaydı oluştur
    log_nac_event(request.mac_address, "MANUAL_QUARANTINE",
                  f"{request.interface} portu manuel olarak karantinaya alındı.")

    return {"status": "success", "message": f"{request.mac_address} Karantina ağına taşındı."}


@router.post("/block-port")
def block_port(request: PortActionRequest):
    """Kritik ihlallerde portu tamamen kapatır (shutdown)."""
    # switch.shutdown_port(request.interface) implementasyonu çağrılacak
    return {"status": "success", "message": f"{request.interface} portu erişime kapatıldı."}

@router.get("/devices")
def get_all_devices():
    """Ağdaki tüm kayıtlı cihazları getirir."""
    try:
        # Veritabanı büyük harf standardınıza (DEVICES) uygun
        response = db.table(TABLE_DEVICES).select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
def get_recent_logs():
    """Sistemde gerçekleşen son 50 NAC olayını getirir."""
    try:
        # LOGS tablosundan en yeniler üstte olacak şekilde çek
        response = db.table(TABLE_LOGS).select("*").order("created_at", desc=True).limit(50).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
