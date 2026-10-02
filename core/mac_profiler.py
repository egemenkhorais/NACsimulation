# core/mac_profiler.py

# Sık kullanılan MAC OUI (İlk 3 Oktet) Veritabanı
OUI_DATABASE = {
    # Apple
    "00:1A:2B": "Apple Device",
    "00:14:51": "Apple Device",
    "BC:53:A0": "MacBook / Apple",
    # Cisco
    "00:24:D7": "Cisco Systems",
    "00:1A:A1": "Cisco Meraki",
    # Sanal Makineler & Geliştirme
    "08:00:27": "VirtualBox VM",
    "00:0C:29": "VMware Node",
    "00:50:56": "VMware Node",
    # IoT ve Diğer
    "B8:27:EB": "Raspberry Pi",
    "DC:A6:32": "Raspberry Pi",
    "00:15:5D": "Microsoft (Hyper-V)",
    "E4:A4:71": "Intel Corporate",
}


def get_vendor_from_mac(mac_address: str) -> str:
    """MAC adresinin ilk 3 oktetini alıp üreticiyi döndürür."""
    if not mac_address or len(mac_address) < 8:
        return "Bilinmeyen Donanım"

    # Gelen MAC adresini standart formata (BÜYÜK HARF ve 00:00:00) çevir
    mac_upper = mac_address.strip().upper()
    oui_prefix = mac_upper[:8]  # Örn: AA:BB:CC

    # Veritabanında varsa döndür, yoksa Genel Cihaz de
    return OUI_DATABASE.get(oui_prefix, "Generic Node")