# https://github.com/bryzz42o/Pwnagotchi-fsociety-plugins/blob/main/sigstr.py
import logging
import subprocess  # Import the subprocess module
import os
import json
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import threading  # Import the threading module for timer

# Static Variables
TAG = "[SigStr Plugin]"

class SigStr(plugins.Plugin):
    __author__ = 'bryzz42o'
    __version__ = '1.0.6'
    __license__ = 'GPL3'
    __description__ = 'Plugin to display signal strength as a bar.'
    REFRESH_INTERVAL = 2  # Refresh interval in seconds

    def __init__(self):
        self.strength = 0
        self.symbol_count = 10  # Define the symbol count for the signal strength bar
        self.timer = threading.Timer(self.REFRESH_INTERVAL, self.refresh)  # Create a timer for refreshing

    def on_loaded(self):
        logging.info(TAG + " Plugin loaded")
        self.timer.start()  # Start the timer when the plugin is loaded

    def on_unload(self):
        self.timer.cancel()  # Cancel the timer when the plugin is unloaded

    def on_ui_setup(self, ui):
        ui.add_element('SignalStrength', LabeledValue(color=BLACK, label='Signal', value='',
                                                      position=(0, 205),
                                                      label_font=fonts.Bold, text_font=fonts.Medium))

    def on_ui_update(self, ui):
        signal_strength = self.get_wifi_signal_strength()
        if signal_strength is not None:
            self.strength = signal_strength
            signal_bar = self.generate_signal_bar(self.strength)
            ui.set('SignalStrength', signal_bar)

    def refresh(self):
        self.timer = threading.Timer(self.REFRESH_INTERVAL, self.refresh)  # Reset the timer
        self.timer.start()  # Start the timer again
        plugins.notify(f"{TAG} Refreshing signal strength")  # Log a message indicating refresh

    def generate_signal_bar(self, strength):
        bar_length = int(strength / (100 / self.symbol_count))  # Adjusted to use self.symbol_count
        bar_segments = '░' * bar_length  # Use to represent filled bar segments (white)
        empty_segments = '█' * (self.symbol_count - bar_length)  # Use to represent empty bar segments (black)
        signal_bar = f'|{bar_segments}{empty_segments}|'  # Construct the full signal bar string
        return signal_bar

    def get_wifi_signal_strength(self):
        try:
            command_output = subprocess.check_output(["iw", "dev", "wlan0", "link"], stderr=subprocess.DEVNULL).decode("utf-8")
            signal_strength = int(command_output.split("signal: ")[1].split(" dBm")[0])
            signal_strength_percent = max(0, min(100, (signal_strength + 100) / 50 * 100))
            return signal_strength_percent
        except subprocess.CalledProcessError:
            logging.error(TAG + " Failed to retrieve signal strength")
            return None