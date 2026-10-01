import os
import time
import uuid
import re
import random
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[HATA] .env dosyasinda SUPABASE_URL veya SUPABASE_KEY bulunamadi.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_actual_mac_address():
    "Çalıştığı cihazın gerçek MAC adresini AA:BB:CC:DD:EE:FF formatında çeker."
    mac_num = hex(uuid.getnode()).replace('0x', '').upper()
    mac_num = mac_num.zfill(12)
    return ':'.join(re.findall('..', mac_num))


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# --- 3. NAC MOTORU SINIFI ---
class NACEngine:
    def __init__(self, db_client: Client):
        self.db = db_client

    def authenticate_8021x(self, username, password, mac_address):
        """Kullanıcıyı ve cihaz eşleşmesini doğrular."""
        print(f"\n[BİLGİ] {mac_address} cihazindan 802.1X istegi baslatildi...")
        time.sleep(1)
        print("[BİLGİ] TLS Tuneli kuruluyor ve MS-CHAPv2 ile kimlik dogrulaniyor...")

        try:
            # Kullanıcıyı veritabanından çek
            user_res = self.db.table("USERS").select("*").eq("username", username).execute()
            if not user_res.data:
                return False, "[RED] Kullanici bulunamadi.", None

            user_data = user_res.data[0]

            # Şifre kontrolü
            if user_data.get("password_hash") != password:
                return False, "[RED] Hatali sifre.", None

            # Cihazı veritabanından çek ve MAC Binding kontrolü yap
            device_res = self.db.table("DEVICES").select("*").eq("mac_address", mac_address).execute()
            if not device_res.data:
                return False, "[RED] Cihaz agda kayitli degil (Rogue MAC).", None

            device_data = device_res.data[0]

            # Cihazın sahibi bu kullanıcı mı?
            if device_data.get("owner_id") != user_data.get("id"):
                return False, f"[GÜVENLİK İHLALİ] MAC Binding hatasi. {username} kullanicisi bu cihazin sahibi degil!", None

            return True, "[BAŞARILI] Kimlik ve cihaz eslesmesi dogrulandi.", device_data

        except Exception as e:
            return False, f"[SİSTEM HATASI] Veritabani sorgusu basarisiz: {str(e)}", None

    def assess_posture(self, device_data):
        """Cihazın sağlık ve yama durumunu kontrol eder."""
        print("[BİLGİ] Posture Assessment (Saglik Taramasi) baslatiliyor...")
        time.sleep(1)

        if not device_data.get("av_active"):
            return "critical", "[RİSK] Antivirus aktif degil."

        if device_data.get("missing_patches", 0) > 0:
            return "warning", f"[UYARI] Cihazda {device_data.get('missing_patches')} adet eksik yama tespit edildi."

        return "clean", "[BAŞARILI] Cihaz temiz ve guncel."

    def analyze_network_flow(self, mac_address):
        """
        Modelin, cihazın ağ trafiğini (network flow) izleyip saldırı olup
        olmadığını analiz ettiği otomasyon katmanını simüle eder.
        """
        print("[BİLGİ] Ag trafigi dinleniyor...")
        time.sleep(1)
        print("[BİLGİ] Egitilmis dataset uzerinden network flow analiz ediliyor (Anomali & Saldiri Tespiti)...")
        time.sleep(2)

        # Simülasyon: %5 ihtimalle ağ trafiğinde saldırı/anomali tespit edilsin
        anomaly_detected = random.choices([True, False], weights=[5, 95])[0]

        if anomaly_detected:
            return True, "[GÜVENLİK İHLALİ] Yapay zeka modeli ag trafiginde supheli saldiri paterni tespit etti!"
        return False, "[BAŞARILI] Ag akisi temiz, saldiri veya anomali saptanmadi."

    def enforce_policy(self, device_id, auth_status, posture_status, flow_attack_status):
        """Elde edilen tüm verilere göre nihai VLAN atamasını gerçekleştirir."""
        assigned_vlan = 99  # Varsayılan: İzolasyon

        if not auth_status or flow_attack_status:
            assigned_vlan = 99
            decision = "Erisim Engellendi -> İzolasyon (VLAN 99)"
        elif posture_status == "critical":
            assigned_vlan = 99
            decision = "Antivirus kapali -> İzolasyon (VLAN 99)"
        elif posture_status == "warning":
            assigned_vlan = 66
            decision = "Eksik yamalar -> Karantina / Remediation (VLAN 66)"
        else:
            assigned_vlan = 10
            decision = "Tam Erisim -> Uretim Agi (VLAN 10)"

        # Kararı veritabanına yaz
        try:
            self.db.table("devices").update({"assigned_vlan": assigned_vlan}).eq("id", device_id).execute()
        except Exception:
            pass  # Hata yönetimi genişletilebilir

        return assigned_vlan, decision


# --- 4. ANA TERMİNAL ARAYÜZÜ ---
def main():
    clear_screen()
    print("=" * 60)
    print(" KURUMSAL NAC - AĞ ERİŞİM KONTROL SİSTEMİ ".center(60))
    print("=" * 60)

    username = input("Kullanici Adi (802.1X): ")
    password = input("Sifre: ")
    mac_address = get_actual_mac_address()

    print("-" * 60)
    engine = NACEngine(supabase)

    # Adım 1: Kimlik Doğrulama
    auth_success, auth_msg, device_data = engine.authenticate_8021x(username, password, mac_address)
    print(auth_msg)

    if not auth_success:
        print("\n[SONUÇ] NAC KARARI: İzolasyon Agi (VLAN 99)")
        print("=" * 60)
        return

    # Adım 2: Sağlık Taraması
    posture_status, posture_msg = engine.assess_posture(device_data)
    print(posture_msg)

    # Adım 3: AI Ağ Akışı Analizi (Sürekli İzleme Otomasyonu Simülasyonu)
    flow_attack_detected, flow_msg = engine.analyze_network_flow(mac_address)
    print(flow_msg)

    # Adım 4: Politika Uygulama ve VLAN Ataması
    print("-" * 60)
    print("[BİLGİ] Nihai karar uygulaniyor...")
    time.sleep(1)

    vlan, decision_msg = engine.enforce_policy(
        device_data.get("id"),
        auth_success,
        posture_status,
        flow_attack_detected
    )

    print(f"[SONUÇ] NAC KARARI: {decision_msg}")
    print("=" * 60)


if __name__ == "__main__":
    main()