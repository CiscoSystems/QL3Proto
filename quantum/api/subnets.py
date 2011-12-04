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


class Controller(common.QuantumController):
    """ Subnet API controller for Quantum API """

    _subnet_ops_param_list = [{
        'param-name': 'cidr',
        'required': True}, ]

    _serialization_metadata = {
        "application/xml": {
            "attributes": {
                "subnet": ["id", "cidr", "network_id"],
                "association": ["routetable_id"]},
            "plurals": {"subnets": "subnet"}},
    }

    def __init__(self, plugin):
        self._resource_name = 'subnet'
        super(Controller, self).__init__(plugin)

    def _item(self, req, tenant_id, subnet_id,
              subnet_details=True):
        subnet = self._plugin.get_subnet_details(
                            tenant_id, subnet_id)
        builder = subnets_view.get_view_builder(req)
        result = builder.build(subnet, subnet_details)['subnet']
        return dict(subnet=result)

    def _items(self, req, tenant_id, subnet_details=False):
        """ Returns a list of subnets. """
        subnets = self._plugin.get_all_subnets(tenant_id)
        builder = subnets_view.get_view_builder(req)
        result = [builder.build(subnet, subnet_details)['subnet']
                  for subnet in subnets]
        return dict(subnets=result)

    def index(self, request, tenant_id):
        """ Returns a list of subnet ids """
        return self._items(request, tenant_id)

    def show(self, request, tenant_id, id):
        """ Returns subnet details for the given subnet id """
        try:
            return self._item(request, tenant_id, id,
                              subnet_details=True)
        except exception.SubnetNotFound as e:
            return faults.Fault(faults.SubnetNotFound(e))

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

    def create(self, request, tenant_id):
        """ Creates a new subnet for a given tenant """
        try:
            request_params = \
                self._parse_request_params(request,
                                           self._subnet_ops_param_list)
        except exc.HTTPError as e:
            return faults.Fault(e)
        try:
            LOG.debug("create() request_params: %s", request_params)
            cidr = request_params['cidr']
            #subnet = self._plugin.\
            #           create_subnet(tenant_id, cidr, **request_params)
            subnet = self._plugin.\
                       create_subnet(tenant_id, **request_params)
        except exception.InvalidCIDR as invalidcidr:
            return faults.Fault(faults.InvalidCIDR(invalidcidr))
        except exception.DuplicateCIDR as duplicatecidr:
            return faults.Fault(faults.DuplicateCIDR(duplicatecidr))
        except exception.NetworkNotFound as notfoundexcp:
            return faults.Fault(faults.NetworkNotFound(notfoundexcp))
        builder = subnets_view.get_view_builder(request)
        result = builder.build(subnet)['subnet']
        return self._build_response(request, dict(subnet=result), 200)

    def update(self, request, tenant_id, id):
        """ Updates the name for the subnet with the given id """
        try:
            request_params = \
                self._parse_request_params(request,
                                           self._subnet_ops_param_list)
        except exc.HTTPError as e:
            return faults.Fault(e)
        try:
            self._plugin.update_subnet(tenant_id, id,
                                        **request_params)
            return exc.HTTPNoContent()
        except exception.SubnetNotFound as e:
            return faults.Fault(faults.SubnetNotFound(e))
        except exception.InvalidCIDR as invalidcidr:
            return faults.Fault(faults.InvalidCIDR(invalidcidr))
        except exception.DuplicateCIDR as duplicatecidr:
            return faults.Fault(faults.DuplicateCIDR(duplicatecidr))
        except exception.NetworkNotFound as notfoundexcp:
            return faults.Fault(faults.NetworkNotFound(notfoundexcp))

    def delete(self, request, tenant_id, id):
        """ Destroys the subnet with the given id """
        try:
            self._plugin.delete_subnet(tenant_id, id)
            return exc.HTTPNoContent()
        except exception.SubnetNotFound as e:
            return faults.Fault(faults.SubnetNotFound(e))
