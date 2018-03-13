
# pp-manager - PythonPlugin Manager
#
# Author: ycahome, 2018
#
#  Since (2018-02-23): Initial Version
#
#
"""
<plugin key="PP-MANAGER" name="Python Plugin Manager" author="ycahome" version="1.5.1" externallink="https://www.domoticz.com/forum/viewtopic.php?f=65&t=22339">
    <description>
		<h2>Python Plugin Manager v.1.5.1</h2><br/>
		<h3>Features</h3>
		<ul style="list-style-type:square">
			<li>Install plugins</li>
			<li>Update All/Selected plugins</li>
			<li>Update Notification for All/Selected</li>
		</ul>
		<h3>----------------------------------------------------------------------</h3>
		<h3>WARNING:</h3>
		<h2>         Auto Updating plugins without verifying their code</h2>
		<h2>         makes you system vulnerable to developer's code intensions!!</h2>
		<h3>----------------------------------------------------------------------</h3>
		<h2>NOTE: After selectiong your options press "Update" button!!</h2>
    </description>
     <params>
        <param field="Mode2" label="Domoticz Plugin" width="200px">
            <options>
                <option label="Idle" value="Idle"  default="true" />
                <option label="Dummy Plugin" value="Dummy_Plugin"/>
                <option label="Battery monitoring for Z-Wave nodes" value="BatteryLevel"/>
                <option label="Buienradar.nl (Weather lookup)" value="Buienradar"/>
                <option label="Denon/Marantz Amplifier" value="Denon4306"/>
                <option label="Disc usage" value="xfr_discusage"/>
                <option label="Dutch earthquakes" value="xfr_aardbeving"/>
                <option label="Eartquake EMSC Data" value="SeismicPortal"/>
                <option label="ebusd bridge" value="ebusd"/>
                <option label="Global Cache 100" value="GC-100"/>
                <option label="Homewizard" value="Homewizard"/>
                <option label="Hive Plugin" value="HivePlug"/>
                <option label="Meteo Alarm EU RSS Reader" value="MeteoAlarmEU"/>
                <option label="Mikrotik RouterOS" value="mikrotik-routeros"/>
                <option label="Moon Phases" value="MoonPhases"/>
                <option label="MQTT discovery" value="MQTTDiscovery"/>
                <option label="Onkyo AV Receiver" value="Onkyo"/>
                <option label="OpenAQ" value="xfr_openaq"/>
                <option label="Pi-hole summary" value="xfr_pihole"/>
                <option label="PiMonitor" value="xfr-pimonitor"/>
                <option label="SNMP Reader" value="SNMPreader"/>
                <option label="Sonos Players" value="Sonos"/>
                <option label="Sony Bravia TV (with Kodi remote)" value="sony"/>
                <option label="Speedtest" value="xfr_speedtest"/>
                <option label="SYSFS-Switches" value="SYSFS-Switches"/>
                <option label="UPS Monitor" value="NUT_UPS"/>
                <option label="Wan IP Checker" value="WAN-IP-CHECKER"/>
                <option label="Xiaomi Mi Flower Mate" value="Mi_Flower_mate_plugin"/>
                <option label="Xiaomi Mi Robot Vacuum" value="xiaomi-mi-robot-vacuum"/>
                <option label="Xiaomi PM2.5 Sensor" value="XiaomiPM"/>
                <option label="Yamaha AV Receiver" value="YamahaPlug"/>
            </options>
        </param>
         <param field="Mode4" label="Auto Update" width="175px">
            <options>
                <option label="All" value="All"/>
                <option label="All (NotifyOnly)" value="AllNotify" default="true"/>
                <option label="Selected" value="Selected"/>
                <option label="Selected (NotifyOnly)" value="SelectedNotify"/>
                <option label="None" value="None"/>
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

import urllib
import urllib.request
import urllib.error
import re

import time

import platform

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
        self.ExceptionList = []

        self.plugindata = {
            # Plugin Key:          [gitHub author,        repository,                  plugin Text]
            "Idle":                         ["Idle",            "Idle",                                 "Idle"],
            "Dummy_Plugin":                 ["ycahome",         "Dummy_Plugin",                         "Dummy Plugin"],
            "BatteryLevel":  			    ["999LV",           "BatteryLevel",                         "Battery monitoring for Z-Wave nodes"],
            "Buienradar":   			    ["ffes",            "domoticz-buienradar",                  "Buienradar.nl (Weather lookup)"],
            "Denon4306":                  	["dnpwwo",    	    "Domoticz-Denon-Plugin",                "Denon/Marantz Amplifier"],
            "xfr_discusage":                ["Xorfor",    	    "Domoticz-Disc-usage-Plugin",           "Disc usage"],
            "xfr_aardbeving":               ["Xorfor",    	    "Domoticz-LastDutchEarthquake-Plugin",  "Dutch earthquakes"],
            "SeismicPortal":                ["febalci",    	    "DomoticzEarthquake",                   "Eartquake EMSC Data"],
            "ebusd":                     	["guillaumezin",    "DomoticzEbusd",                        "ebusd bridge"],
            "GC-100":                     	["dnpwwo",          "Domoticz-GlobalCache-Plugin",          "Global Cache 100"],
            "Homewizard":                   ["rvdvoorde",       "domoticz-homewizard",                  "Homewizard"],
            "HivePlug":                     ["imcfarla2003",    "domoticz-hive",                        "Hive Plugin"],
            "MeteoAlarmEU":                 ["ycahome",         "MeteoAlarmEU",                         "Meteo Alarm EU RSS Reader"],
            "mikrotik-routeros":            ["mrin",            "domoticz-routeros-plugin",             "Mikrotik RouterOS"],
            "MoonPhases":                   ["ycahome",         "MoonPhases",                           "Moon Phases"],
            "MQTTDiscovery":                ["emontnemery",     "domoticz_mqtt_discovery",              "MQTT discovery"],
            "Onkyo":                		["jorgh6",          "domoticz-onkyo-plugin",                "Onkyo AV Receiver"],
            "xfr_openaq":                   ["Xorfor",          "Domoticz-OpenAQ-Plugin",               "OpenAQ"],
            "xfr_pihole":                  	["Xorfor",          "Domoticz-Pi-hole-Plugin",              "Pi-hole summary"],
            "xfr-pimonitor":                ["Xorfor",          "Domoticz-PiMonitor-Plugin",            "PiMonitor"],
            "SNMPreader":                   ["ycahome",         "SNMPreader",                           "SNMP Reader"],
            "Sonos":                    	["gerard33",        "sonos",                                "Sonos Players"],
            "sony":                         ["gerard33",        "sony-bravia",                          "Sony Bravia TV (with Kodi remote)"],
            "xfr_speedtest":                ["Xorfor",          "Domoticz-Speedtest-Plugin ",           "Speedtest"],
            "SYSFS-Switches":               ["flatsiedatsie",   "GPIO-SYSFS-Switches",                  "SYSFS-Switches"],
            "NUT_UPS":                      ["999LV",           "NUT_UPS",                              "UPS Monitor"],
            "WAN-IP-CHECKER":               ["ycahome",         "WAN-IP-CHECKER",                       "Wan IP Checker"],
            "Mi_Flower_mate_plugin":        ["flatsiedatsie",   "Mi_Flower_mate_plugin",                "Xiaomi Mi Flower Mate"],
            "xiaomi-mi-robot-vacuum":       ["mrin",            "domoticz-mirobot-plugin",              "Xiaomi Mi Robot Vacuum"],
            "XiaomiPM":                     ["febalci",         "DomoticzXiaomiPM2.5",                  "Xiaomi PM2.5 Sensor"],
            "YamahaPlug":                   ["thomas-villagers","domoticz-yamaha",                      "Yamaha AV Receiver"],
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

        Domoticz.Log("Domoticz Node Name is:" + platform.node())
        Domoticz.Log("Domoticz Platform System is:" + platform.system())
        Domoticz.Debug("Domoticz Platform Release is:" + platform.release())
        Domoticz.Debug("Domoticz Platform Version is:" + platform.version())
        Domoticz.Log("Default Python Version is:" + str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2]) + ".")

        if platform.system() == "Windows":
            Domoticz.Error("Windows Platform NOT YET SUPPORTED!!")
            return


        pluginText = ""
        pluginAuthor = ""
        pluginRepository = ""
        pluginKey = ""

        pluginKey = Parameters["Mode2"]
        pluginAuthor = self.plugindata[pluginKey][0]
        pluginRepository = self.plugindata[pluginKey][1]
        pluginText = self.plugindata[pluginKey][2]

        Domoticz.Debug("Parsing Script TEST on:" + str(os.getcwd()) + "/plugins/PP-MANAGER/plugin.py")
        parseFileForIP(str(os.getcwd()) + "/plugins/PP-MANAGER/plugin.py")
        
        Domoticz.Debug("Checking for Exception file on:" + str(os.getcwd()) + "/plugins/PP-MANAGER/exceptions.txt")
        if (os.path.isfile(str(os.getcwd()) + "/plugins/PP-MANAGER/exceptions.txt") == True):
            Domoticz.Log("Exception file found. Processing!!!")

            # Open the file
            f = open(str(os.getcwd()) + "/plugins/PP-MANAGER/exceptions.txt")

            # use readline() to read the first line 
            line = f.readline()

            while line:

                if ((line[:1].strip() != "#") and (line[:1].strip() != " ") and (line[:1].strip() != "")):
                    Domoticz.Log("File ReadLine result:'" + line.strip() + "'")
                    self.ExceptionList.append(line.strip())    
                # use realine() to read next line
                line = f.readline()
            f.close()
        Domoticz.Log("self.ExceptionList:" + str(self.ExceptionList))

        if Parameters["Mode4"] == 'All':
            Domoticz.Log("Updating All Plugins!!!")
            i = 0
            path = str(os.getcwd()) + "/plugins/"
            for (path, dirs, files) in os.walk(path):
                for dir in dirs:
                    if str(dir) != "":
                        if str(dir) in self.plugindata:
                            self.UpdatePythonPlugin(pluginAuthor, pluginRepository, str(dir))
                        elif str(dir) == "PP-MANAGER":
                            Domoticz.Debug("PP-Manager Folder found. Skipping!!")      
                        else:
                            Domoticz.Log("Plugin:" + str(dir) + " cannot be managed with PP-Manager!!.")      
                i += 1
                if i >= 1:
                   break

        if Parameters["Mode4"] == 'AllNotify':
            Domoticz.Log("Collecting Updates for All Plugins!!!")
            i = 0
            path = str(os.getcwd()) + "/plugins/"
            for (path, dirs, files) in os.walk(path):
                for dir in dirs:
                    if str(dir) != "":
                        if str(dir) in self.plugindata:
                            self.CheckForUpdatePythonPlugin(pluginAuthor, pluginRepository, str(dir))
                        elif str(dir) == "PP-MANAGER":
                            Domoticz.Debug("PP-Manager Folder found. Skipping!!")      
                        else:
                            Domoticz.Log("Plugin:" + str(dir) + " cannot be managed with PP-Manager!!.")      
                i += 1
                if i >= 1:
                   break

        if (Parameters["Mode4"] == 'SelectedNotify'): 
                Domoticz.Log("Collecting Updates for Plugin:" + pluginKey)
                self.CheckForUpdatePythonPlugin(pluginAuthor, pluginRepository, pluginKey)
           

        if pluginKey == "Idle":
            Domoticz.Log("Plugin Idle")
            Domoticz.Heartbeat(60)
        else:
            Domoticz.Debug("Checking for dir:" + str(os.getcwd()) + "/plugins/" + pluginKey)
            #If plugin Directory exists
            if (os.path.isdir(str(os.getcwd()) + "/plugins/" + pluginKey)) == True:
                Domoticz.Debug("Folder for Plugin:" + pluginKey + " already exists!!!")
                #Domoticz.Debug("Set 'Python Plugin Manager'/ 'Domoticz plugin' attribute to 'idle' in order t.")
                if Parameters["Mode4"] == 'Selected':
                    Domoticz.Log("Updating Enabled for Plugin:" + pluginText + ".Checking For Update!!!")
                    self.UpdatePythonPlugin(pluginAuthor, pluginRepository, pluginKey)
                Domoticz.Heartbeat(60)
            else:
               Domoticz.Log("Installation requested for Plugin:" + pluginText)
               Domoticz.Debug("Installation URL is:" + "https://github.com/" + pluginAuthor +"/" + pluginRepository)
               Domoticz.Debug("Current Working dir is:" + str(os.getcwd()))
               if pluginKey in self.plugindata:
                    Domoticz.Log("Plugin Display Name:" + pluginText)
                    Domoticz.Log("Plugin Author:" + pluginAuthor)
                    Domoticz.Log("Plugin Repository:" + pluginRepository)
                    Domoticz.Log("Plugin Key:" + pluginKey)
                    self.InstallPythonPlugin(pluginAuthor, pluginRepository, pluginKey)
               Domoticz.Heartbeat(60)
            


    def onStop(self):
        Domoticz.Debug("onStop called")

        Domoticz.Log("Plugin is stopping.")
        self.UpdatePythonPlugin("ycahome", "pp-manager", "PP-MANAGER")
        Domoticz.Debugging(0)

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")

        CurHr = str(datetime.now().hour)
        CurMin = str(datetime.now().minute)
        if len(CurHr) == 1: CurHr = "0" + CurHr
        if len(CurMin) == 1: CurMin = "0" + CurMin
        Domoticz.Debug("Current time:" + CurHr + ":" + CurMin)

        if (mid(CurHr,0,2) == "12" and  mid(CurMin,0,2) == "00"):
            Domoticz.Log("Its time!!. Trigering Actions!!!")


            #-------------------------------------
            if Parameters["Mode4"] == 'All':
                Domoticz.Log("Updating All Plugins!!!")
                i = 0
                path = str(os.getcwd()) + "/plugins/"
                for (path, dirs, files) in os.walk(path):
                    for dir in dirs:
                        if str(dir) != "":
                            self.UpdatePythonPlugin(self.plugindata[Parameters["Mode2"]][0], self.plugindata[Parameters["Mode2"]][1], str(dir))
                    i += 1
                    if i >= 1:
                       break

            if Parameters["Mode4"] == 'AllNotify':
                Domoticz.Log("Collecting Updates for All Plugins!!!")
                i = 0
                path = str(os.getcwd()) + "/plugins/"
                for (path, dirs, files) in os.walk(path):
                    for dir in dirs:
                        if str(dir) != "":
                            self.CheckForUpdatePythonPlugin(self.plugindata[Parameters["Mode2"]][0], self.plugindata[Parameters["Mode2"]][1], str(dir))
                    i += 1
                    if i >= 1:
                       break

            if Parameters["Mode4"] == 'SelectedNotify':
                Domoticz.Log("Collecting Updates for Plugin:" + pluginKey)
                self.CheckForUpdatePythonPlugin(self.plugindata[Parameters["Mode2"]][0], self.plugindata[Parameters["Mode2"]][1], Parameters["Mode2"])

            #-------------------------------------
            if Parameters["Mode4"] == 'Selected':
                Domoticz.Log("Updating Enabled for Plugin:" + self.plugindata[pluginKey][2])
                self.UpdatePythonPlugin(self.plugindata[Parameters["Mode2"]][0], self.plugindata[Parameters["Mode2"]][1], Parameters["Mode2"])

            #if Parameters["Mode2"] == "Idle":
                #Domoticz.Log("Plugin Idle. No actions to be performed!!!")
 









    # InstallPyhtonPlugin function
    def InstallPythonPlugin(self, ppAuthor, ppRepository, ppKey):
        Domoticz.Debug("InstallPythonPlugin called")


        Domoticz.Log("Installing Plugin:" + self.plugindata[ppKey][2])
        ppUrl = "/usr/bin/git clone -b master https://github.com/" + ppAuthor + "/" + ppRepository + ".git " + ppKey
        Domoticz.Log("Calling:" + ppUrl)
        try:
            pr = subprocess.Popen( ppUrl , cwd = os.path.dirname(str(os.getcwd()) + "/plugins/"), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
            (out, error) = pr.communicate()
            if out:
                   Domoticz.Log("Succesfully installed:" + str(out).strip)
                   Domoticz.Log("---Restarting Domoticz MAY BE REQUIRED to activate new plugins---")
            if error:
                Domoticz.Debug("Git Error:" + str(error))
                if str(error).find("Cloning into") != -1:
                   Domoticz.Log("Plugin " + ppKey + " installed Succesfully")
        except OSError as e:
            Domoticz.Error("Git ErrorNo:" + str(e.errno))
            Domoticz.Error("Git StrError:" + str(e.strerror))

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
    def UpdatePythonPlugin(self, ppAuthor, ppRepository, ppKey):
        Domoticz.Debug("UpdatePythonPlugin called")

        if ppKey == "PP-MANAGER":
           Domoticz.Log("Self Update Initiated")
        elif (self.plugindata[ppKey][2] in self.ExceptionList):
            Domoticz.Log("Plugin:" + self.plugindata[ppKey][2] + " excluded by Exclusion file (exclusion.txt). Skipping!!!")
            return

        Domoticz.Log("Updating Plugin:" + ppKey)
        ppUrl = "/usr/bin/git pull --force"
        Domoticz.Debug("Calling:" + ppUrl + " on folder " + str(os.getcwd()) + "/plugins/" + ppKey)
        try:
            pr = subprocess.Popen( ppUrl , cwd = str(os.getcwd() + "/plugins/" + ppKey), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
            (out, error) = pr.communicate()
            if out:
                Domoticz.Debug("Git Response:" + str(out))
                if str(out).find("Already up-to-date") != -1:
                   Domoticz.Log("Plugin " + ppKey + " already Up-To-Date")
                   #Domoticz.Log("find(error):" + str(str(out).find("error")))
                elif (str(out).find("Updating") != -1) and (str(str(out).find("error")) == "-1"):
                   ppUrl = "chmod "
                   Domoticz.Log("Succesfully pulled gitHub update:" + str(out)[str(out).find("Updating")+8:26] + " for plugin " + ppKey)
                   Domoticz.Log("---Restarting Domoticz MAY BE REQUIRED to activate new plugins---")
                else:
                   Domoticz.Error("Something went wrong with update of " + str(ppKey))
            if error:
                Domoticz.Debug("Git Error:" + str(error.strip()))
                if str(error).find("Not a git repository") != -1:
                   Domoticz.Log("Plugin:" + ppKey + " is not installed from gitHub. Cannot be updated with PP-Manager!!.")
        except OSError as e:
            Domoticz.Error("Git ErrorNo:" + str(e.errno))
            Domoticz.Error("Git StrError:" + str(e.strerror))

        return None





    # UpdateNotifyPyhtonPlugin function
    def CheckForUpdatePythonPlugin(self, ppAuthor, ppRepository, ppKey):
        Domoticz.Debug("CheckForUpdatePythonPlugin called")

        if (self.plugindata[ppKey][2] in self.ExceptionList):
            Domoticz.Log("Plugin:" + self.plugindata[ppKey][2] + " excluded by Exclusion file (exclusion.txt). Skipping!!!")
            return

        Domoticz.Debug("Checking Plugin:" + ppKey + " for updates")
        ppUrl = "/usr/bin/git status -uno"
        Domoticz.Debug("Calling:" + ppUrl + " on folder " + str(os.getcwd()) + "/plugins/" + ppKey)
        try:
            pr = subprocess.Popen( ppUrl , cwd = str(os.getcwd() + "/plugins/" + ppKey), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
            (out, error) = pr.communicate()
            if out:
                Domoticz.Debug("Git Response:" + str(out))
                if str(out).find("up-to-date") != -1:
                   Domoticz.Log("Plugin " + ppKey + " already Up-To-Date")
                   Domoticz.Debug("find(error):" + str(str(out).find("error")))
                elif (str(out).find("Your branch is behind") != -1) and (str(str(out).find("error")) == "-1"):
                   Domoticz.Log("Found that we are behind on plugin " + ppKey)
                   fnSelectedNotify(ppKey)
                elif (str(out).find("Your branch is ahead") != -1) and (str(str(out).find("error")) == "-1"):
                   Domoticz.Debug("Found that we are ahead on plugin " + ppKey + ". No need for update")
                else:
                   Domoticz.Error("Something went wrong with update of " + str(ppKey))
            if error:
                Domoticz.Debug("Git Error:" + str(error.strip()))
                if str(error).find("Not a git repository") != -1:
                   Domoticz.Log("Plugin:" + ppKey + " is not installed from gitHub. Ignoring!!.")
        except OSError as e:
            Domoticz.Error("Git ErrorNo:" + str(e.errno))
            Domoticz.Error("Git StrError:" + str(e.strerror))

        return None



    # fnSelectedNotify function
    def fnSelectedNotify(self, pluginText):
        Domoticz.Debug("fnSelectedNotify called")
        Domoticz.Log("Preparing Notification")
        ServerURL = "http://127.0.0.1:8080/json.htm?param=sendnotification&type=command"
        MailSubject = urllib.parse.quote(platform.node() + ":Domoticz Plugin Updates Available for " + pluginText)
        MailBody = urllib.parse.quote(pluginText + " has updates available!!")
        MailDetailsURL = "&subject=" + MailSubject + "&body=" + MailBody + "&subsystem=email"
        notificationURL = ServerURL + MailDetailsURL
        Domoticz.Debug("ConstructedURL is:" + notificationURL)
        try:
            response = urllib.request.urlopen(notificationURL, timeout = 30).read()
        except urllib.error.HTTPError as err1:
            Domoticz.Error("HTTP Request error: " + str(err1) + " URL: " + notificationURL)
        return
        Domoticz.Debug("Notification URL is :" + str(notificationURL))


        return None

    #
    # Parse an int and return None if no int is given
    #

    def parseIntValue(s):
        Domoticz.Debug("parseIntValue called")

        try:
            return int(s)
        except:
            return None














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


def mid(s, offset, amount):
    Domoticz.Debug("mid called")
    return s[offset:offset+amount]



def parseFileForIP(pyfilename):
    Domoticz.Debug("mid called")
    
    # Open the file
    file = open(pyfilename, "r")

    ips = []
    ips.append([])
    ips.append([])

    lineNum = 0
    for text in file.readlines():
       text = text.rstrip()
       regexFound = re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',text)
       if regex is not None and regex not in ips:
           Domoticz.Log("File Regex result:'" + str(regex) + "'")
           ips[lineNum].append(regexFound)
       lineNum = lineNum + 1

    file.close()
    Domoticz.Log("ips contents are:" + str(regexFound))
    
    

