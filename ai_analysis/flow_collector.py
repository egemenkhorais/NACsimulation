import time
import random
from ai_analysis.anomaly_detector import NetworkAnomalyDetector
from core.policy_engine import PolicyEngine
from database.supabase_client import db, TABLE_DEVICES


class FlowCollector:
    """Ağ akışını otomasyon olarak izleyip model üzerinden saldırı tespiti yapar."""

    def __init__(self):
        self.detector = NetworkAnomalyDetector()

    def start_monitoring(self):
        print("[AI OTOMASYONU] Dataset tabanlı network flow analizi başlatıldı...")

        while True:
            # 1. Ağdaki aktif cihazları Supabase'den çek
            active_devices_res = db.table(TABLE_DEVICES).select("id, mac_address, assigned_vlan").execute()

            if not active_devices_res.data:
                time.sleep(5)
                continue

            for device in active_devices_res.data:
                # Zaten İzolasyon ağındaysa (VLAN 99) trafiğini incelemeye gerek yok
                if device["assigned_vlan"] == 99:
                    continue

                # 2. Gerçek dünyada Zeek veya sFlow'dan alınacak ağ paketi metrikleri (Simülasyon)
                flow_metrics = {
                    "src_mac": device["mac_address"],
                    "packet_size": random.randint(64, 1500),
                    "tcp_flags": "SYN",
                    "destination_port": random.choice([80, 443, 22, 3389])
                }

                # 3. Ağ akışını, dataset ile eğitilmiş modele ilet
                is_attack = self.detector.analyze_flow(flow_metrics)

                # 4. Saldırı tespit edilirse NAC politikasını devreye sok
                if is_attack:
                    print(f" [AI ALARMI] {device['mac_address']} kaynaklı saldırı tespit edildi!")

                    PolicyEngine.evaluate_and_enforce(
                        device_id=device["id"],
                        mac_address=device["mac_address"],
                        is_authenticated=True,
                        posture_status="clean",
                        is_under_attack=True  # Bu parametre cihazı doğrudan VLAN 99'a atar
                    )

            # Analiz döngüsünü 5 saniyede bir tekrarla
            time.sleep(5)