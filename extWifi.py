# https://github.com/Levi-Michael/pwnagotchi-plugins/blob/main/extWifi.py
import logging, time, subprocess
from pwnagotchi.utils import StatusFile
import pwnagotchi.ui.components as components
import pwnagotchi.ui.view as view
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins


class extWifi(plugins.Plugin):
    __author__ = 'A1buS'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = '''extWifi is plugin to change the local wifi chipset off and make place to external wifi 
    antenna(what that already supported) plugin will add/remove one line in config file and reboot.
    [dtoverlay=disable-wifi]

    as i check work fine with Alfa Awus036acm on jayofelony image https://github.com/jayofelony/pwnagotchi
    still working on make it work with Awus036acs and Awus036ach its interface stay wlan0 what dont work at this image.
    
    Awus036acs - small - bettercap api not avilable wlan0 not change to wlan0monm
    Awus036acm - mid - work perfect
    Awus036ach - large - bettercap api not avilable wlan0 not change to wlan0monm
    '''

    def __init__(self):
        self.ready = False
        self.lineExist = False
        logging.info("[extWifi]: extWifi plugin initialize")

    def config_check(self):
        with open('/boot/config.txt', 'r') as file:
            content = file.read()  # Read all content of a file
            # Check if string present in a file
            if 'dtoverlay=disable-wifi' in content:
                self.lineExist = True
                logging.info("[extWifi]: String EXIST in a file")
            if 'dtoverlay=disable-wifi' not in content:
                self.lineExist = False
                logging.info("[extWifi]: String does NOT exist in a file")

    def config_add(self):
        file = open('/boot/config.txt', 'a')  # Open a file in append mode
        file.write('\ndtoverlay=disable-wifi')  # Write some text
        file.close()  # Close the file
        logging.info("[extWifi]: add line [dtoverlay=disable-wifi] to config file- disable local wifi")

    def config_remove(self):
        with open('/boot/config.txt', 'r') as file:
            text = file.read()

        with open('/boot/config.txt', 'w') as file:  # Delete text and Write
            new_text = text.replace('dtoverlay=disable-wifi', '')  # Delete
            file.write(new_text)  # Write
            file.close()
        logging.info("[extWifi]: [dtoverlay=disable-wifi] removed from config file.")

    def restart_pi(slef):
        logging.info("[extWifi]: Rebooting the pwnagotchi.")

        subprocess.call(["shutdown", "-r", "-t", "0"])  # Reboot the the pi

    def on_loaded(self):
        self.config_check()  # Check if config have the disable line

        # Add line to config file
        if not self.lineExist:
            self.config_add()
        if self.lineExist:
            pass

        self.ready = True
        self.config_check()  # Check if config have the disable line
        logging.info("[extWifi]: extWifi plugin loaded.")
        logging.info("[extWifi]: Sleep for 3 sec.")
        time.sleep(3)
        logging.info("[extWifi]: Reboot.")
        self.restart_pi()

    def on_ui_setup(self, ui):
        with ui._lock:
            # add a LabeledValue element to the UI with the given label and value
            # the position and font can also be specified
            ui.add_element('extWifi-status', components.LabeledValue(color=view.BLACK, label='extWifi: ', value='-',
                                                                     position=(ui.width() / 2 - 125, 95),
                                                                     label_font=fonts.Bold, text_font=fonts.Medium))
        logging.info('[extWifi]: ui_setup successfully loaded.')

    def on_ui_update(self, ui):
        if self.lineExist:
            ui.set('extWifi-status', 'ON')

    def on_unload(self, ui):
        self.config_remove()  # Remove element from screen
        self.config_check()  # Check if config have the disable line
        if not self.lineExist:
            with ui._lock:
                ui.remove_element('extWifi-status')
        logging.info('[extWifi]: extWifi successfully Unloaded.')
        logging.info("[extWifi]: Sleep for 3 sec.")
        time.sleep(3)
        logging.info("[extWifi]: Reboot.")
        self.restart_pi()