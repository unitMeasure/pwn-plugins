# pwn-plugins for Pwnagotchi

These files are for educational, research, and personal experimentation only. Use them responsibly with your own devices. I am not liable for any unethical or harmful use.

**Tutorial and additional scripts:** https://github.com/avipars/pwn-to-own

Collection of plugins to make your pwnagotchi better. 

To use these plugins, append this URL to the `main.custom_plugin_repos` array in your `config.toml`:  
`https://github.com/unitMeasure/pwn-plugins/archive/main.zip`


## Plugins

| Plugin           | Description | Config Info |
|------------------|-------------|-------------|
| **sorted_pwn** | View cracked SSIDs and passwords in a searchable table. Combines all potfiles for a unified view. | None required |
| **probeReq** | View Wi-Fi Probe requests on screen (and in your logs too) | None required |
| **memtempV2** | Shows memory usage, temperature, CPU frequency, and more. | `main.plugins.memtempV2.fields = ['mem', 'cpu', 'temp','freq','cpus']` |
| **fix_region** | Change your Pi's region to unlock more Wi-Fi channels. Default region setting and region info available via webhook. | `main.plugins.fix_region.region = "US"` |
| **privacy_nightmare** | Captures eavesdropping metadata. Primarily for educational/awareness purposes. Minor bugs fixed. | None required (optional GPS support) |
| **enable_assocV2** | Toggle association attacks with a button (no touchscreen dependency). | None required |
| **enable_deauthV2** | Toggle deauthentication attacks with a button (no touchscreen dependency). | None required |
| **NoGPSPrivacy** | Fork of `privacy_nightmare` with fixes for non-GPS setups. Captures metadata without needing GPS. | `main.plugins.nogpsprivacy.pn_output_path = "your/path/here"` |

## Known Issues

- `privacy_nightmare` logs frequent warnings if GPS is not set up.
- `NoGPSPrivacy` requires a directory to store probe info and a config entry:  
  `main.plugins.nogpsprivacy.pn_output_path = "your/path/here"`
- Both `privacy_nightmare` and `NoGPSPrivacy` may keep threads alive after plugin unload. To fix: disable the plugin and restart Pwnagotchi.

More on the way! 

Consider supporting my work [here](https://github.com/sponsors/avipars) 