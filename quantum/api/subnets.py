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
from quantum.api import faults
from quantum.api.views import subnets as subnets_view
from quantum.common import exceptions as exception

LOG = logging.getLogger('quantum.api.subnets')


def create_resource(plugin, version):
    controller_dict = {
                        '1.1': [ControllerV11(plugin),
                                ControllerV11._serialization_metadata,
                                common.XML_NS_V11]}
    return common.create_resource(version, controller_dict)


class Controller(common.QuantumController):
    """ Subnet API controller for Quantum API """

    _subnet_ops_param_list = [{
        'param-name': 'cidr',
        'required': True}, ]

    def __init__(self, plugin):
        self._resource_name = 'subnet'
        super(Controller, self).__init__(plugin)

    def _item(self, req, tenant_id, subnet_id,
              subnet_details=True):
        subnet = self._plugin.get_subnet_details(
                            tenant_id, subnet_id)
        builder = subnets_view.get_view_builder(req, self.version)
        result = builder.build(subnet, subnet_details)['subnet']
        return dict(subnet=result)

    def _items(self, req, tenant_id, subnet_details=False):
        """ Returns a list of subnets. """
        subnets = self._plugin.get_all_subnets(tenant_id)
        builder = subnets_view.get_view_builder(req, self.version)
        result = [builder.build(subnet, subnet_details)['subnet']
                  for subnet in subnets]
        return dict(subnets=result)

    @common.APIFaultWrapper()
    def index(self, request, tenant_id):
        """ Returns a list of subnet ids """
        return self._items(request, tenant_id)

    @common.APIFaultWrapper([exception.SubnetNotFound])
    def show(self, request, tenant_id, id):
        """ Returns subnet details for the given subnet id """
        return self._item(request, tenant_id, id,
                          subnet_details=True)

    @common.APIFaultWrapper([exception.SubnetNotFound])
    def detail(self, request, **kwargs):
        tenant_id = kwargs.get('tenant_id')
        subnet_id = kwargs.get('id')
        if subnet_id:
            # show details for a given subnet
            return self._item(request, tenant_id, subnet_id,
                              subnet_details=True)
        else:
            # show details for all subnets
            return self._items(request, tenant_id, subnet_details=True)

    @common.APIFaultWrapper([exception.InvalidCIDR, exception.DuplicateCIDR,
                             exception.NetworkNotFound])
    def create(self, request, tenant_id, body):
        """ Creates a new subnet for a given tenant """
        body = self._prepare_request_body(body, self._subnet_ops_param_list)
        LOG.debug("create() body: %s", body)
        subnet = self._plugin.create_subnet(tenant_id,
                                            body['subnet']['cidr'],
                                            **body)
        builder = subnets_view.get_view_builder(request, self.version)
        result = builder.build(subnet)['subnet']
        return dict(subnet=result)

    @common.APIFaultWrapper([exception.SubnetNotFound, exception.InvalidCIDR,
                             exception.DuplicateCIDR,
                             exception.NetworkNotFound])
    def update(self, request, tenant_id, id, body):
        """ Updates the name for the subnet with the given id """
        body = self._prepare_request_body(body, self._subnet_ops_param_list)
        LOG.debug("update() body: %s", body)
        self._plugin.update_subnet(tenant_id, id, **body['subnet'])

    @common.APIFaultWrapper([exception.SubnetNotFound])
    def delete(self, request, tenant_id, id):
        """ Destroys the subnet with the given id """
        self._plugin.delete_subnet(tenant_id, id)


class ControllerV11(Controller):
    """Subnet resources controller for Quantum v1.1 API
    """
    _serialization_metadata = {
            "attributes": {
                "subnet": ["id", "cidr", "network_id"],
                "association": ["routetable_id"]},
            "plurals": {"subnets": "subnet"}
    }

    def __init__(self, plugin):
        self.version = "1.1"
        super(ControllerV11, self).__init__(plugin)
