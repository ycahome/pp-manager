from api.api_command import APICommand
from plugins import plugins


class Install(APICommand):
    def execute(self, params):
        if params not in plugins:
            self.send_error('Plugin not found')
            return None

        plugin = plugins[params]

        if (plugin.install()):
            self.send_response('Plugin has been succesfully installed. Please restart Domoticz to take effect.')
        else:
            self.send_error('Error occured during plugin installation. Please check Domoticz Log for more details.')
