# Copyright 2011 Cisco Systems, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# @author Sumit Naiksatam
#

import logging

from webob import exc

from quantum.api import api_common as common
from quantum.api.l3 import l3faults
from quantum.api.l3.views import routetables as routetables_view
from quantum.common.l3 import l3exceptions as exception

LOG = logging.getLogger('quantum.api.routetables')


def create_resource(plugin, version):
    controller_dict = {
                        '1.1': [ControllerV11(plugin),
                                ControllerV11._serialization_metadata,
                                common.XML_NS_V11]}
    return common.create_resource(version, controller_dict)


class Controller(common.QuantumController):
    """ Routetable API controller for Quantum API """

    _routetable_ops_param_list = [{
        'param-name': 'label',
        'required': False},
        {
        'param-name': 'description',
        'required': False}, ]

    def __init__(self, plugin):
        self._resource_name = 'routetable'
        super(Controller, self).__init__(plugin)

    def _item(self, req, tenant_id, routetable_id,
              routetable_details=True):
        routetable = self._plugin.get_routetable_details(
                            tenant_id, routetable_id)
        builder = routetables_view.get_view_builder(req, self.version)
        result = builder.build(routetable, routetable_details)['routetable']
        return dict(routetable=result)

    def _items(self, req, tenant_id, routetable_details=False):
        """ Returns a list of routetables. """
        routetables = self._plugin.get_all_routetables(tenant_id)
        builder = routetables_view.get_view_builder(req, self.version)
        result = [builder.build(routetable, routetable_details)['routetable']
                  for routetable in routetables]
        return dict(routetables=result)

    @common.APIFaultWrapper()
    def index(self, request, tenant_id):
        """ Returns a list of routetable ids """
        return self._items(request, tenant_id)

    @common.L3APIFaultWrapper([exception.RoutetableNotFound])
    def show(self, request, tenant_id, id):
        """ Returns routetable details for the given routetable id """
        return self._item(request, tenant_id, id, routetable_details=True)

    @common.L3APIFaultWrapper([exception.RoutetableNotFound])
    def detail(self, request, **kwargs):
        tenant_id = kwargs.get('tenant_id')
        routetable_id = kwargs.get('id')
        if routetable_id:
            # show details for a given routetable
            return self._item(request, tenant_id, routetable_id,
                              routetable_details=True)
        else:
            # show details for all routetables
            return self._items(request, tenant_id, routetable_details=True)

    @common.APIFaultWrapper()
    def create(self, request, tenant_id, body):
        """ Creates a new routetable for a given tenant """
        body = self._prepare_request_body(body,
                                          self._routetable_ops_param_list)
        LOG.debug("create() body: %s", body)
        routetable = self._plugin.\
                     create_routetable(tenant_id, **body)
        builder = routetables_view.get_view_builder(request, self.version)
        result = builder.build(routetable)['routetable']
        return dict(routetable=result)

    @common.L3APIFaultWrapper([exception.RoutetableNotFound])
    def update(self, request, tenant_id, id, body):
        """
        Updates the label and/or description for the routetable
        with the given id
        """
        body = self._prepare_request_body(body,
                                          self._routetable_ops_param_list)
        LOG.debug("update() body: %s", body)
        self._plugin.update_routetable(tenant_id, id, **body['routetable'])

    @common.L3APIFaultWrapper([exception.RoutetableNotFound])
    def delete(self, request, tenant_id, id):
        """ Destroys the routetable with the given id """
        self._plugin.delete_routetable(tenant_id, id)


class ControllerV11(Controller):
    """Routetable resources controller for Quantum v1.1 API
    """

    _serialization_metadata = {
            "attributes": {
                "routetable": ["id", "label", "description"],
                "route": ["id", "source", "destination", "target"]},
            "plurals": {"routetables": "routetable",
                        "routes": "route"}
    }

    def __init__(self, plugin):
        self.version = "1.1"
        super(ControllerV11, self).__init__(plugin)
