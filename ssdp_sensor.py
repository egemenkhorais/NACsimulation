import socket
import re
import requests


def ssdp_discover_deep():
    SSDP_ADDR = "239.255.255.250"
    SSDP_PORT = 1900

    request = (
        "M-SEARCH * HTTP/1.1\r\n"
        f"HOST: {SSDP_ADDR}:{SSDP_PORT}\r\n"
        "MAN: \"ssdp:discover\"\r\n"
        "MX: 3\r\n"
        "ST: upnp:rootdevice\r\n"
        "\r\n"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(10.0)

    try:
        sock.sendto(request.encode('utf-8'), (SSDP_ADDR, SSDP_PORT))
        print("📡 [Derin SSDP Modu] Android ve IoT cihazların XML kimlikleri avlanıyor...\n")

        while True:
            try:
                data, addr = sock.recvfrom(2048)
                response = data.decode('utf-8', errors='ignore')

                # Cihazın XML dosyasını sakladığı URL'yi (Location) yakala
                location_match = re.search(r'Location:\s*(http[^\r\n]+)', response, re.IGNORECASE)

                if location_match:
                    xml_url = location_match.group(1).strip()

                    try:
                        # 2. AŞAMA: Hedef cihaza sızıp donanım XML'ini indir!
                        xml_resp = requests.get(xml_url, timeout=2).text

                        # XML'in içinden Marka ve Tam Modeli acımasızca kopar
                        model_match = re.search(r'<modelName>(.*?)</modelName>', xml_resp, re.IGNORECASE)
                        vendor_match = re.search(r'<manufacturer>(.*?)</manufacturer>', xml_resp, re.IGNORECASE)

                        if model_match:
                            vendor = vendor_match.group(1) if vendor_match else "Bilinmeyen Üretici"
                            model = model_match.group(1)

                            print(f"[+] HEDEF DEŞİFRE EDİLDİ -> IP: {addr[0]}")
                            print(f"    🔗 XML Kaynağı : {xml_url}")
                            print(f"    📱 TAM DONANIM : {vendor} {model}\n")

                    except requests.exceptions.RequestException:
                        pass  # URL'ye ulaşılamazsa sessizce atla

            except socket.timeout:
                print("🛑 Dinleme tamamlandı.")
                break
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    ssdp_discover_deep()