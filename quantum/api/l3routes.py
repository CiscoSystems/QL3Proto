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
from quantum.api.views import l3routes as routes_view
from quantum.common import exceptions as exception

LOG = logging.getLogger('quantum.api.routes')


def create_resource(plugin, version):
    controller_dict = {
                        '1.1': [ControllerV11(plugin),
                                ControllerV11._serialization_metadata,
                                common.XML_NS_V11]}
    return common.create_resource(version, controller_dict)


class Controller(common.QuantumController):
    """ Routes API controller for Quantum API """

    _route_ops_param_list = [{
        'param-name': 'source',
        'required': True},
        {'param-name': 'destination',
        'required': True},
        {'param-name': 'target',
        'required': False}]

    def __init__(self, plugin):
        self._resource_name = 'route'
        super(Controller, self).__init__(plugin)

    def _item(self, req, tenant_id, routetable_id, route_id,
              route_details=True):
        """ Returns the details of a route """
        route = self._plugin.get_route_details(tenant_id, routetable_id,
                                               route_id)
        builder = routes_view.get_view_builder(req, self.version)
        result = builder.build(route, route_details)['route']
        return dict(route=result)

    def _items(self, req, tenant_id, routetable_id, route_details=False):
        """ Returns a list of routes. """
        routes = self._plugin.get_all_routes(tenant_id, routetable_id)
        builder = routes_view.get_view_builder(req, self.version)
        result = [builder.build(route, route_details)['route']
                  for route in routes]
        return dict(routes=result)

    @common.APIFaultWrapper()
    def index(self, request, tenant_id, routetable_id):
        """ Returns a list of routes for this routetable """
        return self._items(request, tenant_id, routetable_id,
                           route_details=True)

    @common.APIFaultWrapper([exception.RoutetableNotFound,
                             exception.RouteNotFound])
    def show(self, request, tenant_id, routetable_id, id):
        """ Returns route details for the given route id """
        return self._item(request, tenant_id, routetable_id, id,
                          route_details=True)

    @common.APIFaultWrapper([exception.RoutetableNotFound,
                             exception.RouteNotFound])
    def detail(self, request, **kwargs):
        tenant_id = kwargs.get('tenant_id')
        routetable_id = kwargs.get('routetable_id')
        route_id = kwargs.get('id')
        if route_id:
            # show details for a given route
            return self._item(request, tenant_id, routetable_id, route_id,
                              route_details=True)
        else:
            # show details for all routes
            return self._items(request, tenant_id, routetable_id,
                               route_details=True)

    @common.APIFaultWrapper([exception.RoutetableNotFound,
                             exception.RouteSourceInvalid,
                             exception.RouteDestinationInvalid,
                             exception.RouteTargetInvalid,
                             exception.DuplicateRoute])
    def create(self, request, tenant_id, routetable_id, body):
        """ Creates a new route in a routetable for a given tenant """
        body = self._prepare_request_body(body, self._route_ops_param_list)
        LOG.debug("create() body: %s", body)
        route = self._plugin.\
                       create_route(tenant_id, routetable_id, 
                                    body['route']['source'],
                                    body['route']['destination'],
                                    body['route']['target'], **body)
        builder = routes_view.get_view_builder(request, self.version)
        result = builder.build(route, route_details=True)['route']
        return dict(route=result)

    @common.APIFaultWrapper([exception.RoutetableNotFound,
                             exception.RouteNotFound])
    def delete(self, request, tenant_id, routetable_id, id):
        """ Deletes the route with the specific route ID """
        self._plugin.delete_route(tenant_id, routetable_id, id)


class ControllerV11(Controller):
    """Route resources controller for Quantum v1.1 API
    """

    _serialization_metadata = {
            "attributes": {
                "route": ["id", "source", "destination", "target"]},
            "plurals": {"routes": "route"}
    }

    def __init__(self, plugin):
        self.version = "1.1"
        super(ControllerV11, self).__init__(plugin)
