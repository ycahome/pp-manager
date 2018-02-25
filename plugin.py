
# pp-manager - PythonPlugin Manager
#
# Author: ycahome, 2018
#
#  version 1.0.0 (2018-02-23): Initial Version
#
#
#
"""
<plugin key="PP-MANAGER" name="Python Plugin Manager" author="ycahome" version="1.1.0" externallink="https://www.domoticz.com/forum/viewtopic.php?f=65&t=22339">
    <description>
		<h2>Python Plugin Manager v.1.0.0</h2><br/>
		<h3>Features</h3>
		<ul style="list-style-type:square">
			<li>has a predefined list of plugins to be installed (for start only 3 valid plugins and one dummy)</li>
			<li>supports only plugins located on GitHub</li>
			<li>performs plugin installation only if plugin directory not exists</li>
			<li>performs plugin installation and prompts you to restart Domoticz in order to activate it.</li>
		</ul>
		<h3>Plugins</h3>
		<ul style="list-style-type:square">
			<li>SNMP Reader</li>
			<li>UPS Monitor</li>
			<li>Xiaomi Mi Flower Mate</li>
			<li>Sonos</li>
		</ul>
    </description>
     <params>
        <param field="Mode2" label="Domoticz Plugin" width="200px">
            <options>
                <option label="Idle" value="Idle"  default="true" />
                <option label="Battery monitoring for Z-Wave nodes" value="Battery monitoring for Z-Wave nodes"/>
                <option label="Buienradar.nl (Weather lookup)" value="Buienradar.nl (Weather lookup)"/>
                <option label="Homewizard" value="Homewizard"/>
                <option label="ebusd bridge" value="ebusd bridge"/>
                <option label="MQTT discovery" value="MQTT discovery"/>
                <option label="Onkyo AV Receiver" value="Onkyo AV Receiver"/>
                <option label="OpenAQ" value="OpenAQ"/>
                <option label="Pi-hole summary" value="Pi-hole summary"/>
                <option label="PiMonitor" value="PiMonitor"/>
                <option label="SYSFS-Switches" value="SYSFS-Switches"/>
                <option label="SNMP Reader" value="SNMP Reader"/>
                <option label="Sonos Players" value="Sonos Players"/>
                <option label="Speedtest" value="Speedtest"/>
                <option label="UPS Monitor" value="UPS Monitor"/>
                <option label="Wan IP Checker" value="Wan IP Checker"/>
                <option label="Xiaomi Mi Flower Mate" value="Xiaomi Mi Flower Mate"/>
                <option label="Xiaomi Mi Robot Vacuum" value="Xiaomi Mi Robot Vacuum"/>
                <option label="Yamaha AV Receiver" value="Yamaha AV Receiver"/>
                <option label="Dummy Plugin" value="Dummy Plugin"/>
            </options>
        </param>
         <param field="Mode4" label="Auto Update" width="75px">
            <options>
                <option label="All" value="All"/>
                <option label="Selected" value="Selected"/>
                <option label="None" value="None"  default="true" />
            </options>
        </param>
         <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import os
import subprocess
import sys

import time
import urllib
import urllib.request
import urllib.error

#from urllib2 import urlopen
from datetime import datetime, timedelta


class BasePlugin:
    enabled = False
    pluginState = "Not Ready"
    sessionCookie = ""
    privateKey = b""
    socketOn = "FALSE"

    def __init__(self):
        self.debug = False
        self.error = False
        self.nextpoll = datetime.now()
        self.pollinterval = 60  #Time in seconds between two polls

        self.plugindata = {
            # Plugin Text:                      [gitHub author,        repository,                  plugin key]
            "Idle":                             ["idle",            "idle",                         "idle"],
            "SNMP Reader":                      ["ycahome",         "SNMPreader",                   "SNMPreader"],
            "NUT_UPS":                          ["999LV",           "NUT_UPS",                      "NUT_UPS"],
            "Xiaomi Mi Flower Mate":            ["flatsiedatsie",   "Mi_Flower_mate_plugin",        "Mi_Flower_mate_plugin"],
            "Sonos Players":                    ["gerard33",        "sonos",                        "Sonos"],
            "Wan IP Checker":                   ["ycahome",         "WAN-IP-CHECKER",               "WAN-IP-CHECKER"],
            "Speedtest":                        ["Xorfor",          "Domoticz-Speedtest-Plugin ",   "xfr_speedtest"],
            "Buienradar.nl (Weather lookup)":   ["ffes",            "domoticz-buienradar",          "Buienradar"],
            "ebusd bridge":                     ["guillaumezin",    "DomoticzEbusd",                "ebusd"],
            "Pi-hole summary":                  ["Xorfor",          "Domoticz-Pi-hole-Plugin",      "xfr_pihole"],
            "SYSFS-Switches":                   ["flatsiedatsie",   "GPIO-SYSFS-Switches",          "SYSFS-Switches"],
            "Yamaha AV Receiver":               ["thomas-villagers", "domoticz-yamaha",             "YamahaPlug"],
            "Onkyo AV Receiver":                ["jorgh6",          "domoticz-onkyo-plugin",        "Onkyo"],
            "Battery monitoring for Z-Wave nodes":  ["999LV",       "BatteryLevel",                 "BatteryLevel"],
            "Homewizard":                       ["rvdvoorde",       "domoticz-homewizard",          "Homewizard"],
            "PiMonitor":                        ["Xorfor",          "Domoticz-PiMonitor-Plugin",    "xfr-pimonitor"],
            "Xiaomi Mi Robot Vacuum":           ["mrin",            "domoticz-mirobot-plugin",      "xiaomi-mi-robot-vacuum"],
            "MQTT discovery":                   ["emontnemery",     "domoticz_mqtt_discovery",      "MQTTDiscovery"],
            "OpenAQ":                           ["Xorfor",          "Domoticz-OpenAQ-Plugin",       "xfr_openaq"],
            "Dummy Plugin":                     ["ycahome",         "Dummy_Plugin",                 "Dummy_Plugin"],
        }        
        
        
        return

    def onStart(self):

        Domoticz.Debug("onStart called")

        if Parameters["Mode6"] == 'Debug':
            self.debug = True
            Domoticz.Debugging(1)
            DumpConfigToLog()
        else:
            Domoticz.Debugging(0)

        pluginText = ""
        pluginAuthor = ""
        pluginRepository = ""
        pluginKey = ""
        
        pluginText = Parameters["Mode2"]
        pluginAuthor = self.plugindata[pluginText][0]
        pluginRepository = self.plugindata[pluginText][1]
        pluginKey = self.plugindata[pluginText][2]



        Domoticz.Debug("Checking for dir:" + str(os.getcwd()) + "/plugins/" + pluginKey)
        if (os.path.isdir(str(os.getcwd()) + "/plugins/" + pluginKey)) == True:
            Domoticz.Error("Folder for Plugin:" + pluginKey + " already exists. Skipping installation!!!")
            Domoticz.Error("Set 'Python Plugin Manager'/ 'Domoticz plugin' attribute to 'idle'.")
            if Parameters["Mode4"] == 'Selected':
                Domoticz.Log("Updating Enabled for Plugin:" + pluginText)
                UpdatePythonPlugin(pluginAuthor, pluginRepository, pluginKey)
            if Parameters["Mode4"] == 'All':
                Domoticz.Log("Updating for All Plugins NOT YET IMPLEMENTED!!")
        elif pluginText == "Idle":
            Domoticz.Log("Plugin Idle")
        else:
           Domoticz.Log("Installation requested for Plugin:" + pluginText)
           Domoticz.Debug("Installation URL is:" + "https://github.com/" + pluginAuthor +"/" + pluginRepository)
           Domoticz.Debug("Current Working dir is:" + str(os.getcwd()))
           if pluginText in self.plugindata:
                Domoticz.Log("Plugin Display Name:" + pluginText)
                Domoticz.Log("Plugin Author:" + pluginAuthor)
                Domoticz.Log("Plugin Repository:" + pluginRepository)
                Domoticz.Log("Plugin Key:" + pluginKey)
                InstallPythonPlugin(pluginAuthor, pluginRepository, pluginKey)
            
        #Domoticz.Heartbeat(int(Parameters["Mode1"]))


    def onStop(self):
        Domoticz.Log("Plugin is stopping.")
        Domoticz.Debugging(0)

    def onHeartbeat(self):

        Domoticz.Debug("onHeartbeat called")







global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
    return



# InstallPyhtonPlugin function
def InstallPythonPlugin(ppAuthor, ppRepository, ppKey):

    Domoticz.Log("Installing Plugin:" + ppRepository)
    ppUrl = "/usr/bin/git clone -b master https://github.com/" + ppAuthor + "/" + ppRepository + ".git " + ppKey
    Domoticz.Log("Calling:" + ppUrl)
    #subprocess.call(["/usr/bin/git clone -b master https://github.com/" + ppAuthor + '/' + ppRepository + '.git ' + ppRepository])
    try:
        pr = subprocess.Popen( ppUrl , cwd = os.path.dirname(str(os.getcwd()) + "/plugins/"), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        (out, error) = pr.communicate()
        if out:
            Domoticz.Log("Git Response:" + str(out))
        if error:
            Domoticz.Log("Git Error:" + str(error.strip()))
    except OSError as e:
        Domoticz.Error("Git ErrorNo:" + str(e.errno))
        Domoticz.Error("Git StrError:" + str(e.strerror))
 
    Domoticz.Log("---Restarting Domoticz REQUIRED to activate new plugins---")
    #try:
    #    pr1 = subprocess.Popen( "/etc/init.d/domoticz.sh restart" , cwd = os.path.dirname(str(os.getcwd()) + "/plugins/"), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    #    (out1, error1) = pr1.communicate()
    #    if out1:
    #        Domoticz.Log("Command Response1:" + str(out1))
    #    if error1:
    #        Domoticz.Log("Command Error1:" + str(error1.strip()))
    #except OSError1 as e1:
    #    Domoticz.Error("Command ErrorNo1:" + str(e1.errno))
    #    Domoticz.Error("Command StrError1:" + str(e1.strerror))


    return None




# UpdatePyhtonPlugin function
def UpdatePythonPlugin(ppAuthor, ppRepository, ppKey):

    Domoticz.Log("Updating Plugin:" + ppRepository + " with ppKey:" + ppKey)
    ppUrl = "/usr/bin/git pull --force"
    Domoticz.Log("Calling:" + ppUrl + " on folder " + str(os.getcwd()) + "/plugins/" + ppKey)
    #subprocess.call(["/usr/bin/git clone -b master https://github.com/" + ppAuthor + '/' + ppRepository + '.git ' + ppRepository])
    try:
        pr = subprocess.Popen( ppUrl , cwd = str(os.getcwd() + "/plugins/" + ppKey), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        (out, error) = pr.communicate()
        if out:
            Domoticz.Log("Git Response:" + str(out))
            if str(out).find("Already up-to-date") != -1:
               Domoticz.Log("Plugin already Up-To-Date")
	    if str(out).find("Updating") != -1:
	       Domoticz.Log("Succesfully pulled gtHub version:" + str(out)[str(out).find("Updating"):26])
        if error:
            Domoticz.Log("Git Error:" + str(error.strip()))
    except OSError as e:
        Domoticz.Error("Git ErrorNo:" + str(e.errno))
        Domoticz.Error("Git StrError:" + str(e.strerror))
 
    Domoticz.Log("---Restarting Domoticz MAY BE REQUIRED to activate new plugins---")
    #try:
    #    pr1 = subprocess.Popen( "/etc/init.d/domoticz.sh restart" , cwd = os.path.dirname(str(os.getcwd()) + "/plugins/"), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    #    (out1, error1) = pr1.communicate()
    #    if out1:
    #        Domoticz.Log("Command Response1:" + str(out1))
    #    if error1:
    #        Domoticz.Log("Command Error1:" + str(error1.strip()))
    #except OSError1 as e1:
    #    Domoticz.Error("Command ErrorNo1:" + str(e1.errno))
    #    Domoticz.Error("Command StrError1:" + str(e1.strerror))


    return None






#
# Parse an int and return None if no int is given
#

def parseIntValue(s):

        try:
            return int(s)
        except:
            return None


def mid(s, offset, amount):
    return s[offset:offset+amount]


