import logging
import json
import os
import asyncio
import _thread

# import pwnagotchi
# import pwnagotchi.utils as utils

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
# from pwnagotchi.bettercap import Client


class NoGPSPrivacy(plugins.Plugin):
    __GitHub__ = "https://github.com/unitMeasure/pwn-plugins/NoGPSPrivacy"
    __author__ = "avipars"
    __author__ = "Improved by avipars, original by glenn@pegden.com.com"
    __version__ = "0.0.1"
    __license__ = "Private (for now)"
    __description__ = "Privacy nightmare without using GPS"
    __name__ = "NoGPSPrivacy"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self.running = True
        self.second_ws_ready = False
        self.pn_count = 0
        self.pn_status = "Waiting..."

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        if "pn_output_path" not in self.options or (
            "pn_output_path" in self.options and self.options["pn_output_path"] is None
        ):
            logging.debug("pn_output_path not set")
            return

        if not os.path.exists(self.options["pn_output_path"]):
            os.makedirs(self.options["pn_output_path"])

    def on_ready(self, agent):
        logging.info(f"[{self.__class__.__name__}] plugin ready")
        self.hook_ws_events(agent)

    def on_wifi_update(self, agent, access_points):
        self.aps_update("WU", agent, access_points)

    def on_association(self, agent, access_point):
        self.aps_update("AS", agent, [access_point])

    def on_deauthentication(self, agent, access_point, client_station):
        self.aps_update("DA", agent, [access_point])

    def on_handshake(self, agent, filename, access_point, client_station):
        self.aps_update("HS", agent, [access_point])

    def on_ui_setup(self, ui):
        try:
            pos = (1, 76)
            ui.add_element(
                "pn_status",
                LabeledValue(
                    color=BLACK,
                    label="",
                    value=f"[{self.__class__.__name__}]: Active",
                    position=pos,
                    label_font=fonts.Small,
                    text_font=fonts.Small,
                ),
            )

            pos = (122, 94)
            ui.add_element(
                "pn_count",
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
            # don't add anything for now


    def on_ui_update(self, ui):
        ui.set("pn_status", "%s" % (self.pn_status))
        ui.set("pn_count", "%s/%s" % (self.pn_count, self.pn_count))

    async def on_event(self, msg):
        jmsg = json.loads(msg)
        logging.info(f"[{self.__class__.__name__}]: Event %s" % (jmsg["tag"]))
        if jmsg["tag"] == "wifi.client.probe":
            self.pn_status = "Probe from %s" % jmsg["data"]["essid"]
            logging.info(
                f"[{self.__class__.__name__}]: !!! Probe !!! %s" % (jmsg))
        if jmsg["tag"] == "wifi.ap.new":
            self.pn_status = "New AP %s" % jmsg["data"]["essid"]
            logging.info(
                f"[{self.__class__.__name__}]: !!! NEW AP !!! %s" % (jmsg))
            self.aps_update("NE", None, jmsg["data"])

    def hook_ws_events(self, agent):
        # OK aading a second websocket listener is an ugly approach, but without modifying the core code, I cant think of a better way that starting my own thread with my own websock listener

        self.agent = agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        _thread.start_new_thread(
            self._event_poller, (asyncio.get_event_loop(),))

    def _event_poller(self, loop):
        while True:
            logging.info(f"[{self.__class__.__name__}]: Probe listener up!")
            self.pn_status = "Probe listner up!"
            try:
                loop.create_task(self.agent.start_websocket(self.on_event))
                loop.run_forever()
            except Exception as ex:
                logging.debug("Error while polling via websocket (%s)", ex)

    def aps_update(self, update_type, agent, access_points):
        if self.running:
            if not hasattr(self, "ap_list"):
                self.ap_list = {}

            if len(access_points) > 0:
                for ap in access_points:
                    if "hostname" in ap:
                        hostname = ap["hostname"]
                    else:
                        logging.info(
                            f"[{self.__class__.__name__}]: AP (Debug - %s): %s"
                            % (update_type, str(ap))
                        )
                        hostname = "Unknown-%s" % ap["vendor"]

                    APUID = "%s%%%s" % (hostname, ap["mac"])
                    if APUID in self.ap_list:
                        logging.info(
                            f"[{self.__class__.__name__}]: We already know about %s, so ignoring"
                            % APUID
                        )
                        # TODO: Look at merging metadata here
                    else:
                        logging.info(
                            f"[{self.__class__.__name__}]: NEW AP/mac combo %s" % APUID
                        )
                        logging.info(
                            f"[{self.__class__.__name__}]: AP (%s): %s"
                            % (update_type, hostname)
                        )
                        self.ap_list[APUID] = str(ap)
                        self.pn_status = "AP (%s): %s" % (
                            update_type, hostname)
                        self.pn_count += 1
                        pn_filename = "%s/pn_ap_%s.json" % (
                            self.options["pn_output_path"],
                            hostname,
                        )
                        logging.info(f"saving to {pn_filename} ({hostname})")
                        with open(pn_filename, "w+t") as fp:
                            json.dump(ap, fp)
            else:
                logging.warn(
                    f"[{self.__class__.__name__}]: Empty AP list from %s list is %s"
                    % (update_type, access_points)
                )

    def clients_update(self, access_points):
        pass

    def on_unload(self, ui):
        self.running = False
        with ui._lock:
            try:
                ui.remove_element("pn_status")
                ui.remove_element("pn_count")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")