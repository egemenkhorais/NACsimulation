import os
from netmiko import ConnectHandler


class SwitchController:
    """Ağ cihazlarına komut gönderen fiziksel operasyon katmanı."""

    def __init__(self):
        self.switch_ip = os.getenv("SWITCH_IP", "192.168.1.10")  # Test ortamı IP'si
        self.username = os.getenv("SWITCH_USER", "admin")
        self.password = os.getenv("SWITCH_PASS", "cisco123")
        self.device_type = "cisco_ios"

    def assign_vlan_to_port(self, interface: str, target_vlan: int) -> bool:
        """Belirtilen switch portunun erişim (access) VLAN'ını değiştirir."""
        cisco_device = {
            "device_type": self.device_type,
            "host": self.switch_ip,
            "username": self.username,
            "password": self.password,
            "port": 22
        }

        try:
            net_connect = ConnectHandler(**cisco_device)
            commands = [
                f"interface {interface}",
                f"switchport access vlan {target_vlan}",
                "no shutdown"
            ]
            net_connect.send_config_set(commands)
            net_connect.save_config()  # write memory
            net_connect.disconnect()
            return True
        except Exception as e:
            print(f"[SWITCH HATASI] VLAN değiştirilemedi: {str(e)}")
            return False

    def shutdown_port(self, interface: str) -> bool:
        """Yapay zeka modelinden kritik alarm geldiğinde portu tamamen kapatır."""
        # Benzer netmiko yapısı ile 'shutdown' komutu gönderilir.
        pass