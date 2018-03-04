# pp-manager
Domoticz Python plugin manager


BEWARE, this plugin can be used ONLY ON LINUX SYSTEMS and Raspberry Pi!!!!!!


Hello,

Some thoughts became code.

What if we could use a plugin in order to install other plugins from a list?

So, I did it.

This plugin 
- has a predefined list of plugins to be installed 
- auto updates itself on every self.stop()

To install a plugin: select it on "Domoticz Plugin" field and press update

To continuously update all plugins: Select "All" from "Auto Update" drop-down box and press 

To continuously update selected plugin: Select desired plugin from "Domoticz Plugin" field put "Selected" on "Auto Update" drop-down box and press update

To check all plugins for updates and receive notification email: Select "All (NotifyOnly)" from "Auto Update" drop-down box and press update

To check selected plugin for updates and receive notification email: Select desired plugin from "Domoticz Plugin" field put "Selected (NotifyOnly)" on "Auto Update" drop-down box and press update


- supports only plugins located on GitHub
- performs plugin installation only if plugin directory not exists
- performs plugin installation and prompts you to restart Domoticz in order to activate it.
- self updates every 24 hours
- update selected plugin (ad-hoc update) every 24 hours
 -more plugins added

To install another plugin, just select it and press update.


Pending to be implemented:
 - Uninstall plugins
 - standardise execution of a shell file in order to fulfill individual plugin prerequisites
 - check for updates for currently installed plugins and notify admin
 - implement notifications 
 - 



You can install and test it from GitHub bellow (git tools required):

go to your plugins folder
and execute 

[code]git clone https://github.com/ycahome/pp-manager.git PP-MANAGER[/code]




BEWARE, this is a very early Beta version. Use it on your test server first.
Also, can be used ONLY ON LINUX SYSTEMS and Raspberry Pi!!!!!!


Waiting for your comments!!!!
