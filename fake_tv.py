import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Cihazın gerçek donanım kimliği (XML)
XML_BODY = """<?xml version="1.0"?>
<root xmlns="urn:schemas-upnp-org:device-1-0">
  <device>
    <manufacturer>Samsung Electronics</manufacturer>
    <modelName>Galaxy S24 Ultra</modelName>
    <modelNumber>SM-S928B</modelNumber>
  </device>
</root>"""

# 1. Mini Web Sunucusu (Sensör bu XML'i indirmeye gelecek)
class XMLHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.end_headers()
        self.wfile.write(XML_BODY.encode('utf-8'))
    def log_message(self, format, *args): pass # Terminali kirletmemesi için logları sustur

def run_http_server():
    server = HTTPServer(('0.0.0.0', 8080), XMLHandler)
    server.serve_forever()

# 2. SSDP Dinleyici (Ağa XML'in yerini bağıracak)
def run_ssdp_responder():
    MCAST_GRP = '239.255.255.250'
    MCAST_PORT = 1900
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try: sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except: pass
    sock.bind(('', MCAST_PORT))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MCAST_GRP) + socket.inet_aton('0.0.0.0'))

    print("📱 Sahte Galaxy S24 Ultra ağda aktif. Web sunucusu 8080 portunda çalışıyor...")

    while True:
        data, addr = sock.recvfrom(2048)
        if b"M-SEARCH" in data:
            # Sensöre XML'in URL'sini (Location) veriyoruz
            response = (
                "HTTP/1.1 200 OK\r\n"
                f"Location: http://127.0.0.1:8080/desc.xml\r\n"
                "ST: upnp:rootdevice\r\n"
                "\r\n"
            )
            sock.sendto(response.encode('utf-8'), addr)

if __name__ == "__main__":
    threading.Thread(target=run_http_server, daemon=True).start()
    run_ssdp_responder()