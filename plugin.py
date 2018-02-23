
# pp-manager - PythonPlugin Manager
#
# Author: ycahome, 2018
#
#  version 1.0.0 (2018-02-23): Initial Version
#
#
#
"""
<plugin key="PP-MANAGER" name="Python Plugin Manager" author="ycahome" version="1.0.0" externallink="https://www.domoticz.com/forum/viewtopic.php?t=16266">
    <params>
        <param field="Mode2" label="Domoticz Plugin" width="200px">
            <options>
                <option label="Idle" value="Idle"  default="true" />
                <option label="SNMP Reader" value="SNMP Reader"/>
                <option label="UPS Monitor" value="UPS Monitor"/>
                <option label="Dummy Plugin" value="Dummy Plugin"/>
            </options>
        </param>
        <param field="Mode3" label="Notifications" width="75px">
            <options>
                <option label="Notify" value="Notify"/>
                <option label="Disable" value="Disable"  default="true" />
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
#import commands

import hashlib
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
            # Plugin Text:      [author,        repository,             version]
            "idle":             ["idle",        "idle",                 "1.0.0"],
            "SNMP Reader":      ["ycahome"      "SNMPreader",           "1.1.1"],
            "NUT_UPS":          ["999LV",       "NUT_UPS",              "1.1.2"],
            "Dummy_Plugin":     ["ycahome",     "Dummy_Plugin",         "1.1.3"],
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
        gitHubName = ""
        gitHubName = Parameters["Mode2"]
        
        if gitHubName in self.plugindata:
            Domoticz.Log("Plugin Text:" + gitHubName)
            Domoticz.Log("Plugin Author:" + self.plugindata[gitHubName][0])
            Domoticz.Log("Plugin Repository:" + self.plugindata[gitHubName][1])
            Domoticz.Log("Plugin Version:" + self.plugindata[gitHubName][2])
            #self.plugindata[gitHubName][2] = data
        
        Domoticz.Log("Installation requested for Plugin:" + gitHubName)
        Domoticz.Debug("Installation URL is:" + "https://github.com/ycahome/" + gitHubName)
        Domoticz.Log("Current Working dir is:" + str(os.getcwd()))

        Domoticz.Debug("Checking for dir:" + str(os.getcwd()) + "/plugins/" + gitHubName)
        if (os.path.isdir(str(os.getcwd()) + "/plugins/" + gitHubName)) == True:
            Domoticz.Log("Folder for Plugin:" + gitHubName + " already exists")
        else:
            Domoticz.Log("Installing Plugin:" + gitHubName)
            Domoticz.Log("Calling:" + str('git clone -b master https://github.com/ycahome/' + gitHubName + '.git ' + gitHubName))
            #subprocess.call(['/usr/bin/git clone -b master https://github.com/ycahome/' + gitHubName + '.git ' + gitHubName])
            #try:
            #    pr = subprocess.Popen( "/usr/bin/git clone -b master https://github.com/ycahome/" + gitHubName + ".git " + gitHubName , cwd = os.path.dirname(str(os.getcwd()) + "/plugins/"), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
            #    (out, error) = pr.communicate()
            #    if out:
            #        Domoticz.Log("Git Response:" + str(out))
            #    if error:
            #        Domoticz.Log("Git Error:" + str(error.strip()))
            #except OSError as e:
            #    Domoticz.Error("Git ErrorNo:" + str(e.errno))
            #    Domoticz.Error("Git StrError:" + str(e.strerror))

        Domoticz.Debug("Checking for file:" + str(os.getcwd()) + "/plugins/" + gitHubName + "/plugin.py")
        if (os.path.exists(str(os.getcwd()) + "/plugins/" + gitHubName + "/plugin.py")) == True:
            Domoticz.Log("Folder for Plugin:" + gitHubName + " already exists")
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


