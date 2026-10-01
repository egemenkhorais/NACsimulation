class PostureService:
    """Cihazların sağlık ve güvenlik politikalarına uygunluğunu denetler."""

    @staticmethod
    def evaluate_health(device_data: dict) -> str:
        """
        Cihazın antivirüs ve yama (patch) durumunu değerlendirir.

        Dönen değerler:
        - 'clean': Tam erişim verilebilir.
        - 'warning': Karantina ve iyileştirme (remediation) gerekir.
        - 'critical': Ağa girişi tamamen izole edilmelidir.
        """
        # Antivirüs kapalıysa doğrudan kritik risk (İzolasyon)
        if not device_data.get("av_active", False):
            return "critical"

        # Eksik yamalar varsa uyarı seviyesi (Karantina)
        missing_patches = device_data.get("missing_patches", 0)
        if missing_patches > 0:
            return "warning"

        # Sistem temiz
        return "clean"