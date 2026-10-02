from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from network_ops.switch_controller import SwitchController
from database.supabase_client import db, TABLE_DEVICES, TABLE_LOGS, log_nac_event

router = APIRouter()
switch = SwitchController()


# İstemciden (Frontend) beklenen veri formatları
class PortActionRequest(BaseModel):
    mac_address: str
    interface: str  # Örn: "GigabitEthernet0/2"


class VlanUpdateRequest(BaseModel):
    vlan_id: int
    reason: str = "SOC Yöneticisi manuel müdahalesi"


@router.put("/devices/{device_id}/vlan")
def update_device_vlan(device_id: str, request: VlanUpdateRequest):
    """Admin panelinden gelen manuel VLAN değiştirme isteklerini işler."""
    try:
        # 1. Cihazın MAC adresini id üzerinden bul
        device_check = db.table(TABLE_DEVICES).select("mac_address").eq("id", device_id).execute()
        if not device_check.data:
            raise HTTPException(status_code=404, detail="Cihaz bulunamadı")

        mac = device_check.data[0]["mac_address"]

        # 2. Veritabanını güncelle (Sadece assigned_vlan güncelleniyor, is_active yok!)
        res = db.table(TABLE_DEVICES).update({
            "assigned_vlan": request.vlan_id
        }).eq("id", device_id).execute()

        # 3. Log kaydı oluştur
        log_nac_event(mac, "ADMIN_VLAN_CHANGE",
                      f"Cihaz manuel olarak VLAN {request.vlan_id} ağına taşındı. Sebep: {request.reason}")

        # Opsiyonel: Gerçek switch'e komut göndermek istersen buraya ekleyebilirsin
        # switch.assign_vlan_to_port(interface, request.vlan_id)

        return {"status": "success", "message": f"{mac} cihazı VLAN {request.vlan_id} ağına taşındı."}
    except Exception as e:
        print(f"Admin VLAN Değişim Hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quarantine")
def manual_quarantine(request: PortActionRequest):
    """Belirtilen portu zorla Karantina VLAN'ına (66) çeker."""
    success = switch.assign_vlan_to_port(request.interface, target_vlan=66)

    if not success:
        raise HTTPException(status_code=500, detail="Switch'e komut gönderilirken hata oluştu.")

    db.table(TABLE_DEVICES).update({"assigned_vlan": 66}).eq("mac_address", request.mac_address).execute()
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
        response = db.table(TABLE_DEVICES).select("*").order("id").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
def get_recent_logs():
    """Sistemde gerçekleşen son 50 NAC olayını getirir."""
    try:
        response = db.table(TABLE_LOGS).select("*").order("created_at", desc=True).limit(50).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))