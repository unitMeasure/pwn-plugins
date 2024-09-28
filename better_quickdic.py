#https://github.com/itsdarklikehell/pwnagotchi-plugins/blob/master/better_quickdic.py
from pwnagotchi import plugins
import logging
import subprocess
import string
import re
import pwnagotchi.plugins as plugins
import qrcode
import io
import os


class BetterQuickDic(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), silentree12th"
    __version__ = "1.4.6"
    __license__ = "GPL3"
    __description__ = "Run a quick dictionary scan against captured handshakes."
    __name__ = "BetterQuickDic"
    __help__ = "Run a small aircrack scan against captured handshakes and PMKID"
    __dependencies__ = {
        "pip": ["qrcode"],
        "apt": ["aircrack-ng"],
    }
    __defaults__ = {
        "enabled": False,
        "wordlist_folder": "/home/pi/wordlists/",
        "face": "(·ω·)",
        "api": None,
        "id": None,
    }

    def __init__(self):
        self.ready = False
        self.text_to_set = ""
        logging.debug(f"[{self.__class__.__name__}] plugin init")

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        if "face" not in self.options:
            self.options["face"] = "(·ω·)"
        if "wordlist_folder" not in self.options:
            self.options["wordlist_folder"] = "/home/pi/wordlists/"
        if "enabled" not in self.options:
            self.options["enabled"] = False
        if "api" not in self.options:
            self.options["api"] = None
        if "id" not in self.options:
            self.options["id"] = None

        check = subprocess.run(
            ("/usr/bin/dpkg -l aircrack-ng | grep aircrack-ng | awk '{print $2, $3}'"),
            shell=True,
            stdout=subprocess.PIPE,
        )
        check = check.stdout.decode("utf-8").strip()
        if check != "aircrack-ng <none>":
            logging.info(f"[{self.__class__.__name__}] Found %s" % check)
        else:
            logging.warn(
                f"[{self.__class__.__name__}] aircrack-ng is not installed!")


    def on_handshake(self, agent, filename, access_point, client_station):
        display = agent.view()
        result = subprocess.run(
            (
                "/usr/bin/aircrack-ng "
                + filename
                + " | grep \"1 handshake\" | awk '{print $2}'"
            ),
            shell=True,
            stdout=subprocess.PIPE,
        )
        result = result.stdout.decode("utf-8").translate(
            {ord(c): None for c in string.whitespace}
        )
        if not result:
            logging.info(f"[{self.__class__.__name__}] No handshake")
        else:
            logging.info(f"[{self.__class__.__name__}] Handshake confirmed")
            result2 = subprocess.run(
                (
                    "aircrack-ng -w `echo "
                    + self.options["wordlist_folder"]
                    + "*.txt | sed 's/ /,/g'` -l "
                    + filename
                    + ".cracked -q -b "
                    + result
                    + " "
                    + filename
                    + " | grep KEY"
                ),
                shell=True,
                stdout=subprocess.PIPE,
            )
            result2 = result2.stdout.decode("utf-8").strip()
            logging.info(f"[{self.__class__.__name__}] %s" % result2)
            if result2 != "KEY NOT FOUND":
                key = re.search(r"\[(.*)\]", result2)
                pwd = str(key.group(1))
                self.text_to_set = "Cracked password: " + pwd
                # logging.warn('!!! [quickdic] !!! %s' % self.text_to_set)
                display.set("face", self.options["face"])
                display.set("status", self.text_to_set)
                self.text_to_set = ""
                display.update(force=True)
                # plugins.on('cracked', access_point, pwd)

    def on_ui_update(self, ui):
        if self.text_to_set:
            ui.set("face", self.options["face"])
            ui.set("status", self.text_to_set)
            self.text_to_set = ""

    def on_unload(self, ui):
        with ui._lock:
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")