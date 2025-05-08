# pwn-plugins for Pwnagotchi

Collection of plugins to make your pwnagotchi better

Many are a work in progress and may not work on Jay's latest image

If you want to add this repo to your ```config.toml```. To use these plugins, append this ```https://github.com/unitMeasure/pwn-plugins/archive/main.zip``` to the ```main.custom_plugin_repos``` array.

Tutorial and additional scripts - https://github.com/avipars/pwn-to-own 

## Plugins

sorted_pwn: View your cracked network ssid and passwords in a nice table (with a search bar). This plugin provides a combined view of all your potfiles too!

memtempV2: Shows memory usage and temprarture, but also allows other fields and supports showing any combination of them. Set your fields as such ```main.plugins.memtempV2.fields = ['mem', 'cpu', 'temp','freq','cpus']``` or any possible combination of those. ```freq``` will always show ```1G``` if you have a Pi Zero that has not been overclocked. 

fix_region: Change your pi's region to unlock more wi-fi channels. I added default region and ability to see current region set via webhook. Set your preferred region via ```main.plugins.fix_region.region = "US"```, and change US to any 2 letter valid country code 

privacy_nightmare: Eavesdropping metadata for fun and profit (well, education and awareness mostly). I fixed some minor bugs.

NoGPSPrivacy: (forked from privacy_nightmare to fix bugs and make it work if you don't have a GPS module) for eavesdropping metadata from all around you.

enable_assocV2: Button to enable/disable association attacks (removed any reference and usage of touchscreen devices).

enable_deauthV2: Button to enable/disable deauthentication attacks (removed any reference and usage of touchscreen devices).

## Known Issues

* privacy_nightmare will send a lot of warnings in the logfile if you don't have a GPS set up

* NoGPSPrivacy will not work unless you make a directory to store probe information, and add it to the ```config.toml``` under ```main.plugins.nogpsprivacy.pn_output_path = "your/path/here"```

* privacy_nightmare, NoGPSPrivacy seem to continue running their threads after plugin unload. A temporary solution is to disable the respective plugin and then restart the pwnagotchi. 