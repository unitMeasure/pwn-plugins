import logging
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
from pwnagotchi.bettercap import Client

class probeReq(plugins.Plugin):
    __GitHub__ = "https://github.com/unitMeasure/pwn-plugins/"
    __author__ = "avipars"
    __editor__ = 'avipars'
    __version__ = "0.0.0.3"
    __license__ = "GPL3"
    __description__ = "Listens for Wi-Fi probe requests and displays them on screen and in your logs"
    __name__ = "probeReq"
    __defaults__ = {
        "enabled": False
    }

    def __init__(self):
        self.ready = False
        self.title = ""
        self.running = True
        self.pr_status = "Waiting..."

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_ready(self, agent):
        logging.info(f"[{self.__class__.__name__}] plugin ready")

    def on_ui_setup(self, ui):
        try:
            pos = (1, 76)
            ui.add_element(
                "pr_status",
                LabeledValue(
                    color=BLACK,
                    label="",
                    value=f"[{self.__class__.__name__}]: Active",
                    position=pos,
                    label_font=fonts.Small,
                    text_font=fonts.Small,
                ),
            )
        except Exception as e:
            logging.debug(f"[{self.__class__.__name__}]: Error on_ui_setup: {e}")

    def on_ui_update(self, ui):
        ui.set("pr_status", "%s" % (self.pr_status))

    def on_bcap_wifi_client_probe(self, agent, event):
        """WIFI CLIENT PROBE REQUEST"""
        if not self.running:
            return
        probe = event['data']
        self.pr_status = "Probe: %s" % probe['essid']
        logging.info(f"[{self.__class__.__name__}]: Probe %s" % (probe))

    def on_unload(self, ui):
        self.running = False
        with ui._lock:
            try:
                ui.remove_element("pr_status")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)
