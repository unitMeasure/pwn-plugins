# pwn-plugins for Pwnagotchi

Collection of plugins to make your pwnagotchi better

Many are a work in progress and may not work on Jay's latest image

If you want to add this repo to your ```config.toml```. To use these plugins, append this ```https://github.com/unitMeasure/pwn-plugins/archive/main.zip``` to the ```main.custom_plugin_repos``` array.

Tutorial and additional scripts - https://github.com/avipars/pwn-to-own 

## Known Issues

* agev2 will not work on any image after 2.8.9 (from Jay's repo) as AI functionality has been removed

* memtemp_adv requires psutil to be installed (which may not be available on your device)

* privacy_nightmare will send a lot of warnigns in the logfile if you don't have a GPS set up

* NoGPSPrivacy will not work unless you make a directory to store probe information, and add it to the ```config.toml``` under ```main.plugins.nogpsprivacy.pn_output_path = "your/path/here"```


