import logging
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import Text, Line, LabeledValue
from pwnagotchi.ui.view import BLACK
from pwnagotchi.bettercap import Client
from PIL import ImageFont

class probeReq(plugins.Plugin):
    __GitHub__ = "https://github.com/unitMeasure/pwn-plugins/"
    __author__ = "avipars"
    __editor__ = "avipars"
    __version__ = "0.0.0.4" # from 2.3 beta
    __license__ = "GPL3"
    __description__ = "Listens for Wi-Fi probe requests, displays them on screen and logs them."
    __name__ = "probeReq"
    __defaults__ = {
        "enabled": False,
        "verbose": False,
        "logging": False,
    }

    def __init__(self):
        self.ready = False
        self.title = ""
        self.running = True
        self.pr_status = "Waiting"
        self.pos_x = 0
        self.pos_y = 75
        self.show_verbose = False
        self.log_results = False
        
    def on_loaded(self):
        self.pr_status = "Waiting."
        self.show_verbose = self.options.get("verbose", False)
        self.log_results = self.options.get("logging", False)

    def on_ready(self, agent):
        self.pr_status = "Waiting.."

    def on_ui_setup(self, ui):
        try:
            if "pos_x" in self.options:
                self.pos_x = int(self.options.get("pos_x", 0))
            if "pos_y" in self.options:
                self.pos_y = int(self.options.get("pos_y", 75))

            logging.info(f"[{self.__class__.__name__}] pos_x {self.pos_x} pos_y {self.pos_y}")
            ui.add_element("pr_status", LabeledValue(color=BLACK, value="---", position=(self.pos_x, self.pos_y), label_font=fonts.Small, text_font=fonts.Small))
        except Exception as e:
            logging.debug(f"[{self.__class__.__name__}]: Error on_ui_setup: {e}")

    def on_ui_update(self, ui):
        ui.set("pr_status", "%s" % (self.pr_status))

    def on_bcap_wifi_client_probe(self, agent, event):
        """WIFI CLIENT PROBE REQUEST"""
        if not self.running:
            if "logging" in self.options and self.options["logging"]:
                logging.info(f"[{self.__class__.__name__}]: plugin stopped running")
            return

        probe = event["data"]
        d_name = probe["essid"]
        if self.log_results:
            logging.info(f"[{self.__class__.__name__}]: Probe %s" % (probe))

        
        stat = "pr:%s" % d_name[0:20] # limit essid to 20 chars
        if self.show_verbose:
            stat += " rssi:%s" % probe["rssi"]
            vend = probe["vendor"]

            if vend and len(vend) >= 1: # has a vendor
               stat += "\n" + "v:%s" % vend[0:15] # limit vendor to 15 chars

            stat += "\n" + "mac:%s" % probe["mac"] # full mac address
        
        self.pr_status = stat
       

    def on_unload(self, ui):
        self.running = False
        with ui._lock:
            try:
                ui.remove_element("pr_status")
                if self.log_results:
                    logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)
