
# pp-manager - PythonPlugin Manager
#
# Author: ycahome, 2018
#
#  Since (2018-02-23): Initial Version
#
#


"""
<plugin key="PP-MANAGER" name="Python Plugin Manager" author="ycahome" version="2.0.0" externallink="https://www.domoticz.com/forum/viewtopic.php?f=65&t=22339">
    <description>
		<h2>Python Plugin Manager v.2.0.00</h2><br/>
		<h3>Features:</h3>
		<ul style="list-style-type:square">
			<li>Install plugins</li>
			<li>Update plugins</li>
			<li>Notifications when update is available</li>
		</ul>
    </description>
     <params>
         <param field="Mode4" label="Update Notifications" width="175px">
            <options>
                <option label="Enabled" value="Enabled"/>
                <option label="Disabled" value="Disabled" default="true"/>
            </options>
        </param>
         <param field="Mode5" label="Security Scan (Experimental)" width="75px">
            <options>
                <option label="True" value="True"/>
                <option label="False" value="False"  default="true" />
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
from shutil import copy2
import subprocess
import sys

import urllib
import urllib.request
import urllib.error
import re

import time

import platform

from datetime import datetime, timedelta
from plugins import plugins
from api import APIManager


class BasePlugin:
    def __init__(self):
        self.ui_name = 'plugins-manager'
        self.ExceptionList = []
        self.SecPolUserList = {}

    def onStart(self):
        if Parameters["Mode6"] == 'Debug':
            Domoticz.Debugging(2)
        else:
            Domoticz.Debugging(0)

        Domoticz.Debug("Domoticz Node Name is:" + platform.node())
        Domoticz.Debug("Domoticz Platform System is:" + platform.system())
        Domoticz.Debug("Domoticz Platform Release is:" + platform.release())
        Domoticz.Debug("Domoticz Platform Version is:" + platform.version())
        Domoticz.Debug("Default Python Version is:" + str(sys.version_info[0]) + "." + str(
            sys.version_info[1]) + "." + str(sys.version_info[2]) + ".")

        if platform.system() == "Windows":
            Domoticz.Error("Windows Platform NOT YET SUPPORTED!!")
            return

        self.install_ui()
        self.api_manager = APIManager(Devices)

        if (Parameters["Mode5"] == 'True'):
            self.securityScan()

        # Reading exception file and populating array of values
        exceptionFile = str(os.getcwd()) + "/plugins/PP-MANAGER/exceptions.txt"
        Domoticz.Debug("Checking for Exception file on:" + exceptionFile)

        if (os.path.isfile(exceptionFile) == True):
            Domoticz.Log("Exception file found. Processing!!!")

            # Open the file
            f = open(exceptionFile)

            # use readline() to read the first line
            line = f.readline()

            while line:

                if ((line[:1].strip() != "#") and (line[:1].strip() != " ") and (line[:1].strip() != "")):
                    Domoticz.Log("File ReadLine result:'" + line.strip() + "'")
                    self.ExceptionList.append(line.strip())
                # use realine() to read next line
                line = f.readline()
            f.close()
        Domoticz.Debug("self.ExceptionList:" + str(self.ExceptionList))

    def onStop(self):
        self.uninstall_ui()
        # self.UpdatePythonPlugin("ycahome", "pp-manager", "PP-MANAGER")

    def onDeviceModified(self, unit):
        if (unit == self.api_manager.unit):
            self.api_manager.handle_request(Devices[unit].sValue)
            return

    def onHeartbeat(self):
        if Parameters["Mode4"] == 'Enabled':
            CurHr = str(datetime.now().hour)
            CurMin = str(datetime.now().minute)
            if len(CurHr) == 1:
                CurHr = "0" + CurHr
            if len(CurMin) == 1:
                CurMin = "0" + CurMin

            if (mid(CurHr, 0, 2) == "12" and mid(CurMin, 0, 2) == "00"):
                Domoticz.Debug("Its time!!. Trigering Actions!!!")
                self.checkForUpdates()

    def checkForUpdates(self):
        Domoticz.Debug('Checking if any plugins updates are available')

        for key, plugin in plugins.items():
            if plugin.is_update_available():
                self.fnSelectedNotify(plugin)

    # fnSelectedNotify function
    def fnSelectedNotify(self, plugin):
        Domoticz.Debug("fnSelectedNotify called")
        Domoticz.Log("Preparing Notification")
        ServerURL = "http://127.0.0.1:8080/json.htm?param=sendnotification&type=command"
        MailSubject = urllib.parse.quote(
            platform.node() + ":Domoticz Plugin Updates Available for " + plugin.description)
        MailBody = urllib.parse.quote(
            plugin.description + " has updates available!!")
        MailDetailsURL = "&subject=" + MailSubject + \
            "&body=" + MailBody + "&subsystem=email"
        notificationURL = ServerURL + MailDetailsURL
        Domoticz.Debug("ConstructedURL is:" + notificationURL)

        try:
            urllib.request.urlopen(notificationURL, timeout=30).read()
        except urllib.error.HTTPError as err1:
            Domoticz.Error("HTTP Request error: " +
                           str(err1) + " URL: " + notificationURL)

    def securityScan(self):
        Domoticz.Log("Plugin Security Scan is enabled")

        # Reading secpoluserFile and populating array of values
        secpoluserFile = str(os.getcwd()) + \
            "/plugins/PP-MANAGER/secpoluser.txt"

        Domoticz.Debug("Checking for SecPolUser file on:" + secpoluserFile)
        if (os.path.isfile(secpoluserFile) == True):
            Domoticz.Log("secpoluser file found. Processing!!!")

            # Open the file
            secpoluserFileHandle = open(secpoluserFile)

            # use readline() to read the first line
            line = secpoluserFileHandle.readline()

            while line:
                if mid(line, 0, 4) == "--->":
                    secpoluserSection = mid(line, 4, len(line))
                    Domoticz.Log(
                        "secpoluser settings found for plugin:" + secpoluserSection)
                if ((mid(line, 0, 4) != "--->") and (line.strip() != "") and (line.strip() != " ")):
                    Domoticz.Debug(
                        "SecPolUserList exception (" + secpoluserSection.strip() + "):'" + line.strip() + "'")
                    # SecPolUserList.append(line.strip())
                    # SecPolUserList[secpoluserSection].append(line.strip())
                    if secpoluserSection.strip() not in self.SecPolUserList:
                        self.SecPolUserList[secpoluserSection.strip()] = []
                    self.SecPolUserList[secpoluserSection.strip()].append(
                        line.strip())
                # use realine() to read next line
                line = secpoluserFileHandle.readline()
            secpoluserFileHandle.close()
            Domoticz.Log("SecPolUserList exception:" +
                         str(self.SecPolUserList))
        else:
            self.SecPolUserList = {"Global": []}

        i = 0
        path = str(os.getcwd()) + "/plugins/"
        for (path, dirs, files) in os.walk(path):
            for dir in dirs:
                if str(dir) != "":
                    #self.UpdatePythonPlugin(pluginAuthor, pluginRepository, str(dir))
                    #parseFileForSecurityIssues(str(os.getcwd()) + "/plugins/PP-MANAGER/plugin.py")
                    if (os.path.isfile(str(os.getcwd()) + "/plugins/" + str(dir) + "/plugin.py") == True):
                        self.parseFileForSecurityIssues(
                            str(os.getcwd()) + "/plugins/" + str(dir) + "/plugin.py", str(dir))
            i += 1
            if i >= 1:
                break

    def parseFileForSecurityIssues(self, pyfilename, pypluginid):
        Domoticz.Debug("parseFileForSecurityIssues called")
        secmonitorOnly = False

        if Parameters["Mode5"] == 'Monitor':
            Domoticz.Log("Plugin Security Scan is enabled")
            secmonitorOnly = True

        # Open the file
        file = open(pyfilename, "r")

        ips = {}
        # safeStrings = ["['http://schemas.xmlsoap.org/soap/envelope/', 'http://schemas.xmlsoap.org/soap/encoding/']",
        #               "127.0.0.1",
        #               "http://schemas.xmlsoap.org/soap/envelope/'",
        #               "import json",
        #               "import time",
        #               "import platform",
        #               'import re']

        if pypluginid not in self.SecPolUserList:
            self.SecPolUserList[pypluginid] = []

        lineNum = 1
        #Domoticz.Error("self.SecPolUserList[pypluginid]:" + str(self.SecPolUserList[pypluginid]))
        for text in file.readlines():
            text = text.rstrip()

            #Domoticz.Log("'text' is:'" + str(text))
            regexFound = re.findall(
                r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', text)
            paramFound = re.findall(r'<param field=', text)
            if ((regexFound) and not (paramFound)):
                #regexFound[rex] = regexFound[rex].strip('"]')
                #Domoticz.Error("Security Finding(IPregex):" + str(regexFound) + " LINE: " + str(lineNum) + " FILE:" + pyfilename)
                for rex in range(0, len(regexFound)):
                    if ((str(text).strip() not in self.SecPolUserList["Global"]) and (str(text).strip() not in self.SecPolUserList[pypluginid]) and (str(text).strip() != "") and (mid(text, 0, 1) != "#")):
                        Domoticz.Error("Security Finding(IP):-->" + str(text).strip() +
                                       "<-- LINE: " + str(lineNum) + " FILE:" + pyfilename)
                        #Domoticz.Error("Security Finding(IPr):" + regexFound[rex] + " LINE: " + str(lineNum) + " FILE:" + pyfilename)
                        ips["IP" + str(lineNum)
                            ] = (regexFound[rex], "IP Address")

            #rex = 0
            #regexFound = re.findall('import', text)

            # if regexFound:
                #regexFound[rex] = regexFound[rex].strip('"]')
                #Domoticz.Error("Security Finding(IPregex):" + str(regexFound) + " LINE: " + str(lineNum) + " FILE:" + pyfilename)
            #    for rex in range(0,len(regexFound)):
            #         if ((str(text).strip() not in self.SecPolUserList["Global"]) and (str(text).strip() not in self.SecPolUserList[pypluginid]) and (str(text).strip() != "") and (mid(text,0,1) != "#")):
            #             Domoticz.Error("Security Finding(IMP):-->" + str(text) + "<-- LINE: " + str(lineNum) + " FILE:" + pyfilename)
                        #Domoticz.Error("Security Finding(IPr):" + regexFound[rex] + " LINE: " + str(lineNum) + " FILE:" + pyfilename)
            #             ips["IP" + str(lineNum)] = (regexFound[rex], "Import")

            #rex = 0
            #regexFound = re.findall('subprocess.Popen', text)

            # if regexFound:
                #regexFound[rex] = regexFound[rex].strip('"]')
                #Domoticz.Error("Security Finding(IPregex):" + str(regexFound) + " LINE: " + str(lineNum) + " FILE:" + pyfilename)
            #    for rex in range(0,len(regexFound)):
            #         if ((str(text).strip() not in self.SecPolUserList["Global"]) and (str(text).strip() not in self.SecPolUserList[pypluginid]) and (str(text).strip() != "") and (mid(text,0,1) != "#")):
            #             Domoticz.Error("Security Finding(SUB):-->" + str(text) + "<-- LINE: " + str(lineNum) + " FILE:" + pyfilename)
                        #Domoticz.Error("Security Finding(IPr):" + regexFound[rex] + " LINE: " + str(lineNum) + " FILE:" + pyfilename)
            #             ips["IP" + str(lineNum)] = (regexFound[rex], "Subprocess")

            #rex = 0
            #regexFound = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
            #paramFound = re.findall(r'<param field=',text)

            # if ((regexFound) and not (paramFound)):
                #regexFound[rex] = regexFound[rex].strip('"]')
                #Domoticz.Error("Security Finding(IPregex):" + str(regexFound) + " LINE: " + str(lineNum) + " FILE:" + pyfilename)
            #    for rex in range(0,len(regexFound)):
            #         if ((str(text).strip() not in self.SecPolUserList[pypluginid]) and (str(text).strip() != "") and (mid(text,0,1) != "#")):
            #             Domoticz.Error("Security Finding(HTTP):-->" + str(text) + "<-- LINE: " + str(lineNum) + " FILE:" + pyfilename)
                        #Domoticz.Error("Security Finding(IPr):" + regexFound[rex] + " LINE: " + str(lineNum) + " FILE:" + pyfilename)
            #             ips["IP" + str(lineNum)] = (regexFound[rex], "HTTP Address")

            lineNum = lineNum + 1

        file.close()
        Domoticz.Debug("IPS Table contents are:" + str(ips))


    def install_ui(self):
        Domoticz.Debug('Installing custom pages...')

        copy2('./plugins/PP-MANAGER/frontend/index.html',
              './www/templates/' + self.ui_name + '.html')
        copy2('./plugins/PP-MANAGER/frontend/index.js',
              './www/templates/' + self.ui_name + '.js')

        Domoticz.Debug('Installing custom pages completed.')

    def uninstall_ui(self):
        Domoticz.Debug('Uninstalling custom pages...')

        if os.path.exists('./www/templates/' + self.ui_name + '.html'):
            os.remove('./www/templates/' + self.ui_name + '.html')

        if os.path.exists('./www/templates/' + self.ui_name + '.js'):
            os.remove('./www/templates/' + self.ui_name + '.js')

        Domoticz.Debug('Uninstalling custom pages completed.')


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


def onDeviceModified(Unit):
    global _plugin
    _plugin.onDeviceModified(Unit)


def mid(s, offset, amount):
    #Domoticz.Debug("mid called")
    return s[offset:offset+amount]

