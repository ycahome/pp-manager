define(['app'], function(app) {
    app.component('ppManagerPlugin', {
        templateUrl: 'app/pp-manager/index.html',
        controller: ppManagerController,
    });

    app.component('ppManagerPluginsTable', {
        bindings: {
            plugins: '<',
            onSelect: '&',
            onUpdate: '&'
        },
        template: '<table id="pp-manager-plugins" class="display" width="100%"></table>',
        controller: ppManagerPluginsTableController,
    });

    app.factory('ppManager', function($q, $rootScope, domoticzApi) {
        var deviceIdx = 0;
        var requestsCount = 0;
        var requestsQueue = [];
        var onInit = init();

        $rootScope.$on('device_update', function(e, device) {
            if (device.idx === deviceIdx) {
                handleResponse(JSON.parse(device.Data))
            }
        });

        return {
            sendRequest: sendRequest,
        };

        function init() {
            return domoticzApi.sendRequest({
                type: 'devices',
                displayhidden: 1,
                filter: 'all',
                used: 'all'
            })
                .then(domoticzApi.errorHandler)
                .then(function(response) {
                    if (response.result === undefined) {
                        throw new Error('No Plugin devices found')
                    }

                    var apiDevice = response.result
                        .find(function(device) {
                            return device.HardwareType === 'Python Plugin Manager' && device.Unit === 255
                        })

                    if (!apiDevice) {
                        throw new Error('No API Device found')
                    }

                    return setControlDeviceIdx(apiDevice.idx);
                });
        }

        function setControlDeviceIdx(idx) {
            deviceIdx = idx;

            return domoticzApi.sendCommand('clearlightlog', {
                idx: idx
            }).catch(function() {
                console.log('Unable to clear log for device idx:' + idx)
            });
        }

        function sendRequest(command, params) {
            return onInit.then(function() {
                var deferred = $q.defer();
                var requestId = ++requestsCount;

                var requestInfo = {
                    requestId: requestId,
                    deferred: deferred,
                };

                requestsQueue.push(requestInfo);

                domoticzApi.sendCommand('udevice', {
                    idx: deviceIdx,
                    svalue: JSON.stringify({
                        type: 'request',
                        requestId: requestId,
                        command: command,
                        params: params || {}
                    })
                }).catch(function(error) {
                    deferred.reject(error);
                });

                return deferred.promise;
            });
        }

        function handleResponse(data) {
            if (data.type !== 'response' && data.type !== 'status') {
                return;
            }

            var requestIndex = requestsQueue.findIndex(function(item) {
                return item.requestId === data.requestId;
            });

            if (requestIndex === -1) {
                return;
            }

            var requestInfo = requestsQueue[requestIndex];

            if (data.type === 'status') {
                requestInfo.deferred.notify(data.payload);
                return;
            }

            if (data.isError) {
                requestInfo.deferred.reject(data.payload);
            } else {
                requestInfo.deferred.resolve(data.payload);
            }
            
            requestsQueue.splice(requestIndex, 1);
        }
    });

    function ppManagerController(ppManager) {
        var $ctrl = this
        $ctrl.refreshPlugins = refreshPlugins;

        $ctrl.$onInit = function() {
            refreshPlugins();
        }

        function refreshPlugins() {
            ppManager.sendRequest('list').then(function(plugins) {
                $ctrl.plugins = Object.values(plugins)
            })
        }
    }

    function ppManagerPluginsTableController($element, bootbox, ppManager, dataTableDefaultSettings) {
        var $ctrl = this;
        var table;

        $ctrl.$onInit = function() {
            table = $element.find('table').dataTable(Object.assign({}, dataTableDefaultSettings, {
                order: [[1, 'asc']],
                paging: false,
                columns: [
                    {
                        title: '',
                        data: 'is_installed',
                        width: '20px',
                        orderable: false,
                        render: isInstalledRenderer
                    },
                    { title: 'Description', data: 'description' },
                    { title: 'Author', data: 'author' },
                    { title: 'Plugin Name', data: 'name' },
                    {
                        title: '',
                        className: 'actions-column',
                        width: '80px',
                        data: 'source',
                        orderable: false,
                        render: actionsRenderer
                    },
                ],
            }));

            table.on('click', '.js-install', function() {
                var plugin = table.api().row($(this).closest('tr')).data();

                bootbox.confirm('Are you sure you want to install "' + plugin.description + '" plugin?')
                    .then(function() {
                        return ppManager.sendRequest('install', plugin.key);
                    })
                    .then(bootbox.alert, bootbox.alert)
                    .then($ctrl.onUpdate);
            });

            table.on('click', '.js-update', function() {
                var plugin = table.api().row($(this).closest('tr')).data();

                bootbox.confirm([
                    'Are you sure you want to update "' + plugin.description + '" plugin?',
                    'Updating plugins without verifying their code makes your system vulnerable to developer\'s code intensions!'
                ].join('<br /><br />'))
                    .then(function() {
                        return ppManager.sendRequest('update', plugin.key);
                    })
                    .then(bootbox.alert, bootbox.alert)
                    .then($ctrl.onUpdate);
            });

            render($ctrl.plugins);
        }

        $ctrl.$onChanges = function(changes) {
            if (changes.plugins) {
                render($ctrl.plugins);
            }
        };

        function render(items) {
            if (!table || !items) {
                return;
            }

            table.api().clear();
            table.api().rows
                .add(items)
                .draw();
        }

        function isInstalledRenderer(isInstalled) {
            return isInstalled
                ? '<img src="../../images/ok.png" title="Installed" width="16" height="16" />'
                : '<img src="../../images/empty16.png" width="16" height="16" />'
        }

        function actionsRenderer(data, type, plugin) {
            var actions = [];
            var delimiter = '<img src="../../images/empty16.png" width="16" height="16" />';

            if (!plugin.is_installed) {
                actions.push('<button class="btn btn-icon js-install" title="' + $.t('Install') + '"><img src="images/down.png" /></button>');
            } else if (plugin.is_update_available) {
                actions.push('<button class="btn btn-icon js-update" title="' + $.t('Update') + '"><img src="images/mode.png" /></button>');
            } else {
                actions.push(delimiter)
            }

            actions.push(delimiter)
            actions.push('<a class="btn btn-icon" href="' + plugin.source + '" target="_blank" title="' + $.t('Go to source') + '"><img src="images/details.png" /></a>');
            // actions.push('<button class="btn btn-icon js-rename-device" title="' + $.t('Rename Device') + '"><img src="images/rename.png" /></button>');
            return actions.join('&nbsp;');
        }
    }
});