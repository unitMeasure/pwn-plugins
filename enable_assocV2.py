import os, sys
import logging

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

#https://github.com/Sniffleupagus/pwnagotchi_plugins/pull/6

class enable_assocV2(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com'
    __version__ = '1.0.2.1'
    __editor__ = '(edited by Sniffleupagus then avipars)'
    __license__ = 'GPL3'
    __description__ = 'Enable and disable ASSOC on the fly. Enabled when plugin loads, disabled when plugin unloads. No Touch screen here'

    def __init__(self):
        self._agent = None
        self._count = 0

    # called when the plugin is loaded
    def on_loaded(self):
        self._count = 0
        pass

    # called before the plugin is unloaded
    def on_unload(self, ui):
        try:
            if self._agent:
                self._agent._config['personality']['associate'] = False
            ui.remove_element('assoc_count')
            logging.info("[enable_assocV2] unloading")
        except Exception as e:
            logging.warn(repr(e))

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        self._agent = agent
        agent._config['personality']['associate'] = True
        logging.info("[enable_assocV2] ready: enabled association")


    def on_association(self, agent, access_point):
        self._count += 1

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        self._ui = ui
        # add custom UI elements
        if "position" in self.options:
            pos = self.options['position'].split(',')
            pos = [int(x.strip()) for x in pos]
        else:
            pos = (0,29,30,59)

        ui.add_element('assoc_count', LabeledValue(color=BLACK, label='A', value='0', position=pos,
                                                       label_font=fonts.BoldSmall, text_font=fonts.Small))

        # called when the ui is updated
    def on_ui_update(self, ui):
        # update those elements
        ui.set('assoc_count', "%d" % (self._count))