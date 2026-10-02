OUI_DATABASE = {
    # ---(TEST) ---
    "E2:08:1B": "MacBook / Apple (Private)",

    # --- APPLE (iPhone, iPad, Mac) ---
    "00:1A:2B": "Apple Device",
    "00:14:51": "Apple Device",
    "BC:53:A0": "Apple Device",
    "00:1E:52": "Apple Device",
    "00:23:32": "Apple Device",
    "00:25:00": "Apple Device",
    "88:1F:A1": "Apple Device",
    "F4:0F:24": "Apple Device",

    # --- CISCO & KURUMSAL AĞ ---
    "00:24:D7": "Cisco Systems",
    "00:1A:A1": "Cisco Meraki",
    "00:00:0C": "Cisco Systems",
    "00:14:69": "Cisco Systems",
    "00:1F:CA": "Cisco Systems",
    "00:1B:D4": "Cisco Systems",

    # --- INTEL (Ağ Kartları & PC) ---
    "E4:A4:71": "Intel Corporate",
    "00:15:17": "Intel Corporate",
    "00:1B:21": "Intel Corporate",
    "80:86:F2": "Intel Corporate",
    "F8:34:41": "Intel Corporate",

    # --- SAMSUNG (Telefon, Akıllı TV, Saat) ---
    "00:12:36": "Samsung Electronics",
    "00:09:18": "Samsung Electronics",
    "CC:3A:61": "Samsung Electronics",
    "90:18:7C": "Samsung Electronics",
    "60:6B:BD": "Samsung Electronics",

    # --- HUAWEI ---
    "00:1E:10": "Huawei Technologies",
    "00:25:9E": "Huawei Technologies",
    "00:46:4B": "Huawei Technologies",
    "B4:15:13": "Huawei Technologies",

    # --- MICROSOFT (Windows, Surface, Xbox) ---
    "00:15:5D": "Microsoft (Hyper-V)",
    "00:50:F2": "Microsoft Corporation",
    "28:18:78": "Microsoft Corporation",
    "C0:33:5E": "Microsoft Corporation",
    "30:59:B7": "Microsoft Corporation",

    # --- HP / DELL / LENOVO (PC ve Yazıcılar) ---
    "00:0E:7F": "HP Inc.",
    "00:11:0A": "HP Inc.",
    "00:14:C2": "HP Inc.",
    "00:14:22": "Dell Inc.",
    "00:1E:4F": "Dell Inc.",
    "F8:B1:56": "Dell Inc.",
    "00:12:FE": "Lenovo Group",
    "E0:DB:55": "Lenovo Group",

    # --- XIAOMI & AKILLI EV (IoT) ---
    "00:9E:C8": "Xiaomi Communications",
    "0C:1D:AF": "Xiaomi Communications",
    "14:F6:5A": "Xiaomi Communications",
    "28:E3:1F": "Xiaomi Communications",
    "78:11:DC": "Xiaomi Communications",

    # --- GOOGLE (Chromecast, Pixel, Nest) ---
    "00:1A:11": "Google Nest",
    "3C:5A:B4": "Google Inc.",
    "D8:50:E6": "Google Inc.",
    "F4:F5:D8": "Google Inc.",

    # --- AMAZON (Echo, Alexa, Kindle) ---
    "00:FC:8B": "Amazon Technologies",
    "0C:47:C9": "Amazon Technologies",
    "38:F7:3D": "Amazon Technologies",
    "44:65:0D": "Amazon Technologies",

    # --- SONY & NINTENDO (Oyun Konsolları) ---
    "00:01:4A": "Sony Corporation",
    "00:13:A9": "Sony PlayStation",
    "F8:D0:AC": "Sony PlayStation",
    "00:09:BF": "Nintendo Co.",
    "E0:E7:51": "Nintendo Co.",

    # --- AĞ CİHAZLARI & YONGA SETLERİ ---
    "00:0A:EB": "TP-Link",
    "00:19:E0": "TP-Link",
    "C0:06:C3": "TP-Link",
    "00:0C:6E": "AsusTek Computer",
    "04:D9:F5": "AsusTek Computer",
    "00:10:18": "Broadcom",
    "00:E0:4C": "Realtek Semiconductor",
    "52:54:00": "Realtek / QEMU",

    # --- SANAL MAKİNELER (VM) ---
    "08:00:27": "VirtualBox VM",
    "00:0C:29": "VMware Node",
    "00:50:56": "VMware Node",

    # --- RASPBERRY PI ---
    "B8:27:EB": "Raspberry Pi Foundation",
    "DC:A6:32": "Raspberry Pi Foundation",
    "E4:5F:01": "Raspberry Pi Foundation"
}


def get_vendor_from_mac(mac_address: str) -> str:
    """MAC adresinden üreticiyi veya Private MAC durumunu tespit eder."""
    if not mac_address or len(mac_address) < 8:
        return "Bilinmeyen Donanım"

    mac_upper = mac_address.strip().upper()
    oui_prefix = mac_upper[:8]

    if oui_prefix in OUI_DATABASE:
        return OUI_DATABASE[oui_prefix]

    if len(mac_upper) > 1 and mac_upper[1] in ['2', '6', 'A', 'E']:
        return "Randomized MAC (Gizli)"

    return "Generic Node"