# pwn-plugins for Pwnagotchi

These files are for educational, research, and personal experimentation only. Use them responsibly with your own devices. I am not liable for any unethical or harmful use.

**Tutorial and additional scripts:** https://github.com/avipars/pwn-to-own

Collection of plugins to make your pwnagotchi better. 

To use these plugins, append this URL to the `main.custom_plugin_repos` array in your `config.toml`:  
`https://github.com/unitMeasure/pwn-plugins/archive/main.zip`


## Plugins

| Name          | Description                                                                                                          | Config Info                                                          | Attribution                                                          |
| --------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| sorted_pwn      | View cracked SSIDs and passwords in a searchable table. Combines all potfiles for a unified view.                    | None required                                                        | https://github.com/dbukovac                                          |
| probeReq        | View Wi-Fi Probe requests on screen (and in your logs too)                                                           | None required                                                        | https://github.com/avipars                                           |
| memtempV2       | Shows memory usage, temperature, CPU frequency, and more.                                                            | main.plugins.memtempV2.fields = ['mem', 'cpu', 'temp','freq','cpus'] | https://github.com/xenDE                                             |
| fix_region      | Change your Pi's region to unlock more Wi-Fi channels. Default region setting and region info available via webhook. | main.plugins.fix_region.region = "US"                                | [https://github.com/V0r-T3x](https://github.com/V0r-T3x)             |
| enable_assocV2  | Toggle association attacks with a button (no touchscreen dependency).                                                | None required                                                        | [https://github.com/Sniffleupagus](https://github.com/Sniffleupagus) |
| enable_deauthV2 | Toggle deauthentication attacks with a button (no touchscreen dependency).                                           | None required                                                        | [https://github.com/Sniffleupagus](https://github.com/Sniffleupagus) |
| NoGPSPrivacy    | Fork of privacy_nightmare with fixes for non-GPS setups. Captures metadata without needing GPS.                      | main.plugins.nogpsprivacy.pn_output_path = "your/path/here"          | https://github.com/GlennPegden2                                      |                                 |


I modified and improved most of these plugins to work better for my Pwnagotchi setup and use-case (Jay's 2.9.5.3 image).Some plugins are created from scratch by me as well! 

## Additional and optional config options

### enable_assocV2:

`main.plugins.enable_assocV2.position = "x1,y1,x2,y2"`  - positions the text for number of associations A

Position is in pixels (natural numbers), replace x1,y1,x2,y2 with your desired coordinates. This creates a rectangle on screen where the text will be displayed. Example: `position = "0,29,30,59"`

Changes: I removed the Touchscreen dependency which removes some log errors when touchscreen is not present. (and tried to submit it as a pull request but it was closed)

### enable_deauthV2:

`main.plugins.enable_deauthV2.position = "x1,y1,x2,y2"` - positions the text for number of deauths D

Position is in pixels (natural numbers), replace x1,y1,x2,y2 with your desired coordinates. This creates a rectangle on screen where the text will be displayed. Example: `position = "0,36,30,59"`

`main.plugins.enable_deauthV2.behave_list = "x1,y1,x2,y2"` - list of AP MACs or Hostnames (SSIDs) to not deauth. Separate multiple entries with commas. Example: `behave_list = "00:11:22:33:44:55,MyHomeAP"`

Changes: I removed the Touchscreen dependency which removes some log errors when touchscreen is not present. 

### memtempV2:

`main.plugins.memtempV2.orientation = "vertical"` or `main.plugins.memtempV2.orientation = "horizontal"`

`main.plugins.memtempV2.linespacing = x` where x is an integer (default is 4)

`main.plugins.memtempV2.scale = "fahrenheit"` ,  `main.plugins.memtempV2.scale = "celsius"`, or  `main.plugins.memtempV2.scale = "kelvin"` for measuring CPU temperature

`main.plugins.memtempV2.fields = ['mem', 'cpu', 'temp','freq','cpus']` - choose which fields to display. Options are: 'mem', 'cpu', 'temp','freq','cpus'. Example: `fields = ['mem', 'temp']` will only show memory usage and temperature.

CPUS is true CPU utilization for all cores (Pi Zero 2W for example has 4cores, Pi Zero W has 1 core)

CPU is system load average

FREQ is cpu frequency... usually will show 1ghz on PI Zeros unless you overclock

Changes: I added the ability to allow using more than 3 fields which was a limitation in the original plugin, added support for more screens.

### fix_region:

`main.plugins.fix_region.region = "US"` - set to your desired region code (default is US). Change this to your country's ISO code to unlock more wi-fi channels. Example: "GB" for United Kingdom, "DE" for Germany, etc.

Changes: I added a webhook to show current region (and submitted a pull request which is still open). There are some more features planned for this plugin in a future update.

### NoGPSPrivacy:

`main.plugins.NoGPSPrivacy.save_logs = true` or `main.plugins.NoGPSPrivacy.save_logs = false` - set to true to save logs, false to not save logs (default is false)

Changes: I removed GPS dependency and fixed issues with non-GPS setups (from privacy_nightmare plugin), and when plugin unloads, it will remove the UI elements. Also added option to save logs or not.

### probeReq:

No configuration options at the moment, there will be more options in a future update (position, more details, etc)

Changes: I created this plugin from scratch to show wi-fi probe requests on screen and log them.

### sorted_pwn:

No configuration options at the moment

Changes: It now merge multiple potfiles into one viewable table (combining duplicate entries), also added more fields to the table. 

## Known Issues

- `NoGPSPrivacy` requires a directory to store probe info and a config entry:  

`main.plugins.NoGPSPrivacy.pn_output_path = "your/path/here"`
- `NoGPSPrivacy` may keep threads alive after plugin unloads. To fix: disable the plugin and restart Pwnagotchi or use probeReq instead (no gps and only logs probes) or use probeReq instead! 

## Support My Work

Consider supporting my work [here](https://github.com/sponsors/avipars) 
