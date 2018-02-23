
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
                <option label="NUT UPS" value="NUT UPS"/>
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
import hmac
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
            #DisplayName       (gitHubName,           Version)
            "Idle":       ("Idle",          1), # On line (mains is present)
            "SNMP Reader":       ("SNMPreader",       1), # On battery (mains is not present)
            "UPS Monitor":       ("NUT_UPS",      4), # Low battery
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
        Domoticz.Log("Installation requested for Plugin:" + Parameters["Mode2"])
        Domoticz.Log("Installation URL is:" + "https://github.com/ycahome/" + self.plugindata[gitHubName][1])
        Domoticz.Heartbeat(int(Parameters["Mode1"]))


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


