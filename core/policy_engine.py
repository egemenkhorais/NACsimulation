from database.supabase_client import db, TABLE_DEVICES, log_nac_event


class PolicyEngine:
    """Nihai NAC politikalarını uygulayan karar motoru."""

    @staticmethod
    def evaluate_and_enforce(device_id: str, mac_address: str, is_authenticated: bool, posture_status: str,
                             is_under_attack: bool) -> int:
        assigned_vlan = 99  # Varsayılan değer: İzolasyon Ağı
        reason = ""

        if not is_authenticated:
            assigned_vlan = 99
            reason = "Kimlik doğrulama başarısız"
        elif is_under_attack:
            assigned_vlan = 99
            reason = "AI model ağ akışında saldırı tespit etti (Kritik Güvenlik İhlali)"
        elif posture_status == "critical":
            assigned_vlan = 99
            reason = "Kritik sağlık eksikliği (Antivirüs kapalı)"
        elif posture_status == "warning":
            assigned_vlan = 66
            reason = "Eksik yamalar mevcut (Karantina/Remediation Ağı)"
        else:
            assigned_vlan = 10
            reason = "Tam uyumlu (Üretim Ağı)"

        # Kararı Supabase'e kaydet (Veritabanı büyük harf standartları)
        db.table(TABLE_DEVICES).update({"assigned_vlan": assigned_vlan}).eq("id", device_id).execute()

        # Kararı logla
        log_nac_event(mac_address, "POLICY_ENFORCED", f"Atanan VLAN: {assigned_vlan}. Sebep: {reason}")

        return assigned_vlan