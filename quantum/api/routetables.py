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
from quantum.api.views import routetables as routetables_view
from quantum.common import exceptions as exception

LOG = logging.getLogger('quantum.api.routetables')


class Controller(common.QuantumController):
    """ Routetable API controller for Quantum API """

    _routetable_ops_param_list = [{
        'param-name': 'label',
        'required': False},
        {
        'param-name': 'description',
        'required': False}, ]

    _serialization_metadata = {
        "application/xml": {
            "attributes": {
                "routetable": ["id", "label", "description"],
                "route": ["id", "source", "destination", "target"]},
            "plurals": {"routetables": "routetable",
                        "routes": "route"}},
    }

    def __init__(self, plugin):
        self._resource_name = 'routetable'
        super(Controller, self).__init__(plugin)

    def _item(self, req, tenant_id, routetable_id,
              routetable_details=True):
        routetable = self._plugin.get_routetable_details(
                            tenant_id, routetable_id)
        builder = routetables_view.get_view_builder(req)
        result = builder.build(routetable, routetable_details)['routetable']
        return dict(routetable=result)

    def _items(self, req, tenant_id, routetable_details=False):
        """ Returns a list of routetables. """
        routetables = self._plugin.get_all_routetables(tenant_id)
        builder = routetables_view.get_view_builder(req)
        result = [builder.build(routetable, routetable_details)['routetable']
                  for routetable in routetables]
        return dict(routetables=result)

    def index(self, request, tenant_id):
        """ Returns a list of routetable ids """
        return self._items(request, tenant_id)

    def show(self, request, tenant_id, id):
        """ Returns routetable details for the given routetable id """
        try:
            return self._item(request, tenant_id, id,
                              routetable_details=True)
        except exception.RoutetableNotFound as e:
            return faults.Fault(faults.RoutetableNotFound(e))

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

    def create(self, request, tenant_id):
        """ Creates a new routetable for a given tenant """
        try:
            request_params = \
                self._parse_request_params(request,
                                           self._routetable_ops_param_list)
        except exc.HTTPError as e:
            return faults.Fault(e)
        routetable = self._plugin.\
                     create_routetable(tenant_id, **request_params)
        builder = routetables_view.get_view_builder(request)
        result = builder.build(routetable)['routetable']
        return self._build_response(request, dict(routetable=result), 200)

    def update(self, request, tenant_id, id):
        """
        Updates the label and/or description for the routetable
        with the given id
        """
        try:
            request_params = \
                self._parse_request_params(request,
                                           self._routetable_ops_param_list)
        except exc.HTTPError as e:
            return faults.Fault(e)
        try:
            self._plugin.update_routetable(tenant_id, id,
                                        **request_params)
            return exc.HTTPNoContent()
        except exception.RoutetableNotFound as e:
            return faults.Fault(faults.RoutetableNotFound(e))

    def delete(self, request, tenant_id, id):
        """ Destroys the routetable with the given id """
        try:
            self._plugin.delete_routetable(tenant_id, id)
            return exc.HTTPNoContent()
        except exception.RoutetableNotFound as e:
            return faults.Fault(faults.RoutetableNotFound(e))
