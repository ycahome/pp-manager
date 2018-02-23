
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
                <option label="Xiaomi Mi Flower Mate" value="Xiaomi Mi Flower Mate"/>
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
            # Plugin Text:                      [gitHub author,        repository,                  plugin key]
            "Idle":                             ["idle",            "idle",                         "idle"],
            "SNMP Reader":                      ["ycahome",         "SNMPreader",                   "SNMPreader"],
            "NUT_UPS":                          ["999LV",           "NUT_UPS",                      "NUT_UPS"],
            "Xiaomi Mi Flower Mate":            ["flatsiedatsie",   "Mi_Flower_mate_plugin",        "Mi_Flower_mate_plugin"],
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


