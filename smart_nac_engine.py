from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import asyncio

app = FastAPI(title="ZeroTrust Global Profiler API", version="3.0.0")

# --- API ANAHTARLARI VE YAPILANDIRMA ---
FINGERBANK_API_KEY = "URNOTGETTINGANYTHINGBRO"
MAC_VENDOR_API_URL = "https://api.macvendors.com/"


class DeviceFingerprint(BaseModel):
    mac_address: str
    dhcp_option_55: str | None = None
    dhcp_option_60: str | None = None


# Cihaz kategorisine göre ağ atamaları (Dinamik kural motoru)
VLAN_POLICIES = {
    "smartphone": 77,
    "tablet": 77,
    "computer": 10,  # PC/Mac -> Üretim
    "network_device": 99,  # Switch/Router -> Yönetim
    "voip_phone": 50,  # Ses
    "printer": 30,  # Yazıcı
    "iot": 40,  # Akıllı ev / Kamera
    "game_console": 40,  # Konsollar
}


async def get_mac_vendor_from_global_db(mac: str) -> str:
    """Açık kaynak MAC API'sine giderek üreticiyi bulur."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MAC_VENDOR_API_URL}{mac}", timeout=3.0)
            if response.status_code == 200:
                return response.text.strip()
            return "Unknown Vendor (Or Randomized MAC)"
    except Exception:
        return "MAC API Timeout"


async def get_model_from_fingerbank(dhcp_55: str, mac: str) -> dict:
    """Fingerbank'in devasa veritabanına bağlanıp cihazın spesifik modelini çeker."""
    if not dhcp_55 or FINGERBANK_API_KEY == "URNOTGETTINGANYTHINGBRO":
        return {"model": "Unknown (No DHCP / No API Key)", "category": "unknown"}

    try:
        url = "https://api.fingerbank.org/api/v2/combinations/interrogate"
        headers = {"Authorization": f"Bearer {FINGERBANK_API_KEY}"}

        # Fingerbank'in beklediği sorgu formatı
        payload = {
            "dhcp_fingerprint": dhcp_55,
            "mac": mac
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=5.0)

            if response.status_code == 200:
                data = response.json()
                # Fingerbank eşleşme bulursa modeli ve cihaz tipini döndürür
                if "device" in data and data["device"]:
                    return {
                        "model": data["device"].get("name", "Unknown Model"),
                        "category": data["device"].get("device_class", "unknown")  # örn: 'smartphone'
                    }
            return {"model": "Fingerbank Eşleşmesi Bulunamadı", "category": "unknown"}
    except Exception as e:
        print(f"Fingerbank API Hatası: {e}")
        return {"model": "API Connection Error", "category": "unknown"}


@app.post("/api/v1/profile-and-assign")
async def profile_device(request: DeviceFingerprint):
    """
    Sisteme bir cihaz bağlandığında eşzamanlı (asynchronous) olarak
    dünyadaki açık veritabanlarını tarar ve VLAN kararını verir.
    """
    try:
        mac = request.mac_address.upper()

        # 1. Her iki global API'ye aynı anda (paralel) istek atarak hız kazanıyoruz
        vendor_task = get_mac_vendor_from_global_db(mac)
        model_task = get_model_from_fingerbank(request.dhcp_option_55, mac)

        vendor_result, model_result = await asyncio.gather(vendor_task, model_task)

        # 2. Cihaz kategorisini analiz et ve VLAN'ı belirle
        device_category = model_result["category"].lower()
        assigned_vlan = VLAN_POLICIES.get(device_category, 66)  # Kategori bilinmiyorsa Karantina (66)

        return {
            "mac_address": mac,
            "detected_profile": {
                "vendor_from_mac_db": vendor_result,
                "exact_model": model_result["model"],
                "fingerbank_category": device_category
            },
            "nac_decision": {
                "assigned_vlan": assigned_vlan,
                "action": "PERMIT" if assigned_vlan != 66 else "QUARANTINE",
                "source": "Global API Engines"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)