import socket
import re
import requests


def load_apple_database():
    print("🌍 Apple Donanım Veritabanı (ipsw.me) indiriliyor...")
    try:
        response = requests.get("https://api.ipsw.me/v4/devices", timeout=5)
        devices = response.json()
        hw_map = {}
        for dev in devices:
            name = dev.get("name")
            board = dev.get("boardconfig", "").lower()
            identifier = dev.get("identifier", "").lower()
            if board:
                hw_map[board] = name
            if identifier:
                hw_map[identifier] = name
        print(f"✅ Başarılı! {len(devices)} farklı Apple modeli yüklendi.\n")
        return hw_map
    except Exception as e:
        print(f"⚠️ Apple veritabanı indirilemedi: {e}")
        return {}


def multi_vector_mdns_sniffer(apple_db):
    MCAST_GRP = '224.0.0.251'
    MCAST_PORT = 5353

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass

    sock.bind(('', MCAST_PORT))
    mreq = socket.inet_aton(MCAST_GRP) + socket.inet_aton('0.0.0.0')
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print("📡 [Genişletilmiş Mod] Apple, Linux ve Yazıcı mDNS yayınları dinleniyor...")
    print("Dinleme aktif... (Durdurmak için CTRL+C)\n")

    while True:
        try:
            data, addr = sock.recvfrom(2048)
            raw_text = data.decode('utf-8', errors='ignore')

            # 1. APPLE TESPİTİ (model=D84AP veya model=Mac16,1)
            apple_match = re.search(r'model=([A-Za-z0-9,]+)', raw_text)
            if apple_match:
                raw_code = apple_match.group(1).lower()
                marketing_name = apple_db.get(raw_code, f"Bilinmeyen Apple ({raw_code.upper()})")
                print(f"[+] APPLE CİHAZI YAKALANDI -> IP: {addr[0]}")
                print(f"    Donanım Kodu : {raw_code.upper()}")
                print(f"    Ticari Model : {marketing_name}\n")
                continue

            # 2. YAZICI TESPİTİ (ty=, product=, usb_MDL=)
            printer_match = re.search(r'(?:ty|product|usb_MDL)=([A-Za-z0-9\s\-_/().]+)', raw_text, re.IGNORECASE)
            if printer_match:
                printer_model = printer_match.group(1).strip()
                # Parantez içi temizliği (ör. (HP Color LaserJet))
                printer_model = printer_model.strip('()')
                print(f"[+] YAZICI YAKALANDI -> IP: {addr[0]}")
                print(f"    Yazıcı Modeli: {printer_model}\n")
                continue

            # 3.LINUX ve WOrkstation TESPİTİ (workstation , _ssh)
            if "_workstation" in raw_text or "_ssh" in raw_text:
                # Aralardaki görünmez baytları yakalaması için regex'te '.' kullandık
                host_match = re.search(r'([A-Za-z0-9\-]+)._(workstation|ssh)._tcp', raw_text, re.IGNORECASE)

                if host_match:
                    hostname = host_match.group(1)

                    distro_hint = "Standart Linux Cihazı"
                    lower_name = hostname.lower()
                    if "raspberry" in lower_name:
                        distro_hint = "Raspberry Pi (Raspbian/Debian)"
                    elif "ubuntu" in lower_name:
                        distro_hint = "Ubuntu Workstation"
                    elif "kali" in lower_name:
                        distro_hint = "Kali Linux"
                    elif "arch" in lower_name:
                        distro_hint = "Arch Linux"

                    print(f"[+] LINUX SİSTEM YAKALANDI -> IP: {addr[0]}")
                    print(f"    Hostname   : {hostname}")
                    print(f"    Tahmin     : {distro_hint}\n")

        except Exception:
            pass


if __name__ == "__main__":
    db = load_apple_database()
    multi_vector_mdns_sniffer(db)