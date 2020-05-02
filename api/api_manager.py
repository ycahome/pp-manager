import Domoticz
import json
from api.commands import commands


class APIManager:
    def __init__(self, devices):
        self.unit = 255
        self.devices = devices
        self.requests = {}

        self._create_transport()

    def handle_request(self, request):
        data = json.loads(request)

        if (data['type'] == 'request'):
            request_id = data['requestId']
            Domoticz.Debug('New request: [' + str(request_id) + '] ' +
                           data['command'] + '(' + json.dumps(data['params']) + ')')

            if data['command'] in commands:
                command = commands[data['command']](
                    request_id,
                    self._send_response,
                    self._send_update,
                )

                self.requests.update({request_id: command})
                command.execute(data['params'])
            else:
                self._send_response(data['requestId'], True, 'unknown command')

    def _create_transport(self):
        if self.unit in self.devices:
            return

        Domoticz.Device(
            Unit=self.unit,
            DeviceID='api_transport',
            Name='PP Manager API Transport',
            TypeName="Text"
        ).Create()

    def _update_api_device(self, payload):
        self.devices[self.unit].Update(
            nValue=0,
            sValue=payload
        )

    def _send_response(self, request_id, is_error, payload):
        if request_id in self.requests:
            del self.requests[request_id]

        self._update_api_device(json.dumps({
            'type': 'response',
            'requestId': request_id,
            'isError': is_error,
            'payload': payload
        }))

    def _send_update(self, request_id, payload):
        self._update_api_device(json.dumps({
            'type': 'status',
            'requestId': request_id,
            'payload': payload
        }))
