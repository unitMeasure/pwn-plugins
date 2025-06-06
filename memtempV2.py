# originally from https://github.com/jayofelony/pwnagotchi/blob/noai/pwnagotchi/plugins/default/memtemp.py but modified by me

# MemTempV2 shows memory infos and cpu temperature
#
# mem usage, cpu load, cpu temp, cpu frequency
#
###############################################################
from pwnagotchi.ui.components import LabeledValue, Text
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging


class MemTempV2(plugins.Plugin):
    __author__ = 'https://github.com/xenDE'
    __version__ = '0.0.1'
    __editor__ = 'avipars'
    __license__ = 'GPL3'
    __description__ = 'A plugin that will display memory, cpu usage, load, and temperature, can show as many as you want'

    ALLOWED_FIELDS = {
        'mem': 'mem_usage',
        'cpu': 'cpu_load',
        'cpus': 'cpu_load_since',
        'temp': 'cpu_temp',
        'freq': 'cpu_freq'
    }
    DEFAULT_FIELDS = ['mem', 'cpu', 'temp']
    LINE_SPACING = 10
    LABEL_SPACING = 0
    FIELD_WIDTH = 4
    def __init__(self):
        self.options = dict()

    def on_loaded(self):
        self._last_cpu_load = self._cpu_stat()
        logging.info("MemTempV2 plugin loaded.")

    def mem_usage(self):
        return f"{int(pwnagotchi.mem_usage() * 100)}%"

    def cpu_load(self):
        return f"{int(pwnagotchi.cpu_load() * 100)}%"

    def _cpu_stat(self):
        """
        Returns the split first line of the /proc/stat file
        """
        with open('/proc/stat', 'rt') as fp:
            return list(map(int,fp.readline().split()[1:]))

    def cpu_load_since(self):
        """
        Returns the % load, since last time called
        """
        parts0 = self._cpu_stat()
        parts1 = self._last_cpu_load
        self._last_cpu_load = parts0

        parts_diff = [p1 - p0 for (p0, p1) in zip(parts0, parts1)]
        user, nice, sys, idle, iowait, irq, softirq, steal, _guest, _guest_nice = parts_diff
        idle_sum = idle + iowait
        non_idle_sum = user + nice + sys + irq + softirq + steal
        total = idle_sum + non_idle_sum
        return f"{int(non_idle_sum / total * 100)}%"

    def cpu_temp(self):
        if self.options['scale'] == "fahrenheit":
            temp = (pwnagotchi.temperature(celsius=False))
            symbol = "F"
        elif self.options['scale'] == "kelvin":
            temp = pwnagotchi.temperature() + 273.15
            symbol = "K"
        else:
            # default to celsius
            temp = pwnagotchi.temperature()
            symbol = "C"
        return f"{temp}{symbol}"

    def cpu_freq(self):
        with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq', 'rt') as fp:
            return f"{round(float(fp.readline())/1000000, 1)}G"

    def pad_text(self, data):
        return " " * (self.FIELD_WIDTH - len(data)) + data

    def on_ui_setup(self, ui):
        try:
            # Configure field list
            self.fields = self.options['fields'].split(',')
            self.fields = [x.strip() for x in self.fields if x.strip() in self.ALLOWED_FIELDS.keys()]
            # self.fields = self.fields[:3]  #  removed the 3 first field limit 
        except Exception:
            # Set default value
            self.fields = self.DEFAULT_FIELDS

        try:
            # Configure line_spacing
            line_spacing = int(self.options['linespacing'])
        except Exception:
            # Set default value
            line_spacing = self.LINE_SPACING

        try:
            # Configure position
            pos = self.options['position'].split(',')
            pos = [int(x.strip()) for x in pos]
            if self.options['orientation'] == "vertical":
                v_pos = (pos[0], pos[1])
            else:
                h_pos = (pos[0], pos[1])
        except Exception:
            # Set default position based on screen type
            if ui.is_waveshare_v2() or ui.is_waveshare_v3() or ui.is_waveshare_v4():
                h_pos = (175, 84)
                v_pos = (197, 74)
            elif ui.is_waveshare_v1():
                h_pos = (170, 80)
                v_pos = (165, 61)
            elif ui.is_waveshare144lcd():
                h_pos = (53, 77)
                v_pos = (73, 67)
            elif ui.is_inky():
                h_pos = (140, 68)
                v_pos = (160, 54)
            elif ui.is_waveshare2in7():
                h_pos = (192, 138)
                v_pos = (211, 122)
            elif ui.is_waveshare1in54V2():
                h_pos = (53, 77)
                v_pos = (154, 65)
            else:
                h_pos = (155, 76)
                v_pos = (175, 61)

        if self.options['orientation'] == "vertical":
            # Dynamically create the required LabeledValue objects
            for idx, field in enumerate(self.fields):
                v_pos_x = v_pos[0]
                v_pos_y = v_pos[1] + ((len(self.fields) - 3) * -1 * line_spacing)
                ui.add_element(
                    f"MemTempV2_{field}",
                    LabeledValue(
                        color=BLACK,
                        label=f"{self.pad_text(field)}:",
                        value="-",
                        position=(v_pos_x, v_pos_y + (idx * line_spacing)),
                        label_font=fonts.Small,
                        text_font=fonts.Small,
                        label_spacing=self.LABEL_SPACING,
                    )
                )
        else:
            # default to horizontal
            h_pos_x = h_pos[0] + ((len(self.fields) - 3) * -1 * 25)
            h_pos_y = h_pos[1]
            ui.add_element(
                'MemTempV2_header',
                Text(
                    color=BLACK,
                    value=" ".join([self.pad_text(x) for x in self.fields]),
                    position=(h_pos_x, h_pos_y),
                    font=fonts.Small,
                )
            )
            ui.add_element(
                'MemTempV2_data',
                Text(
                    color=BLACK,
                    value=" ".join([self.pad_text("-") for x in self.fields]),
                    position=(h_pos_x, h_pos_y + line_spacing),
                    font=fonts.Small,
                )
            )

    def on_unload(self, ui):
        with ui._lock:
            try:
                if self.options['orientation'] == "vertical":
                    for idx, field in enumerate(self.fields):
                        ui.remove_element(f"MemTempV2_{field}")
                else:
                    # default to horizontal
                    ui.remove_element('MemTempV2_header')
                    ui.remove_element('MemTempV2_data')
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)

    def on_ui_update(self, ui):
        with ui._lock:
            try:
                if self.options['orientation'] == "vertical":
                    for idx, field in enumerate(self.fields):
                        ui.set(f"MemTempV2_{field}", getattr(self, self.ALLOWED_FIELDS[field])())
                else:
                    # default to horizontal
                    data = " ".join([self.pad_text(getattr(self, self.ALLOWED_FIELDS[x])()) for x in self.fields])
                    ui.set('MemTempV2_data', data)
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)
