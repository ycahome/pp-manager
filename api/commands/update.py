from api.api_command import APICommand
from plugins import plugins


class Update(APICommand):
    def execute(self, params):
        if params not in plugins:
            self.send_error('Plugin not found')
            return None

        plugin = plugins[params]

        if (plugin.update()):
            self.send_response('Plugin has been succesfully updated. Please restart Domoticz to take effect.')
        else:
            self.send_error('Error occured during plugin update. Please check Domoticz Log for more details.')
