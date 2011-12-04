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


class Controller(common.QuantumController):
    """ Routes API controller for Quantum API """

    _route_ops_param_list = [{
        'param-name': 'source',
        'required': True},
        {'param-name': 'destination',
        'required': True},
        {'param-name': 'target',
        'required': False}]

    _serialization_metadata = {
        "application/xml": {
            "attributes": {
                "route": ["id", "source", "destination", "target"]},
            "plurals": {"routes": "route"}},
    }

    def __init__(self, plugin):
        self._resource_name = 'route'
        super(Controller, self).__init__(plugin)

    def _item(self, req, tenant_id, routetable_id, route_id,
              route_details=True):
        """ Returns the details of a route """
        route = self._plugin.get_route_details(tenant_id, routetable_id,
                                               route_id)
        builder = routes_view.get_view_builder(req)
        result = builder.build(route, route_details)['route']
        return dict(route=result)

    def _items(self, req, tenant_id, routetable_id, route_details=False):
        """ Returns a list of routes. """
        routes = self._plugin.get_all_routes(tenant_id, routetable_id)
        builder = routes_view.get_view_builder(req)
        result = [builder.build(route, route_details)['route']
                  for route in routes]
        return dict(routes=result)

    def index(self, request, tenant_id, routetable_id):
        """ Returns a list of routes for this routetable """
        return self._items(request, tenant_id, routetable_id,
                           route_details=True)

    def show(self, request, tenant_id, routetable_id, id):
        """ Returns route details for the given route id """
        try:
            return self._item(request, tenant_id, routetable_id, id,
                              route_details=True)
        except exception.RoutetableNotFound as e:
            return faults.Fault(faults.RoutetableNotFound(e))
        except exception.RouteNotFound as e:
            return faults.Fault(faults.RouteNotFound(e))

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


    def create(self, request, tenant_id, routetable_id):
        """ Creates a new route in a routetable for a given tenant """
        try:
            print("inside routes.py, request: %s", request)
            request_params = \
                self._parse_request_params(request,
                                           self._route_ops_param_list)
        except exc.HTTPError as e:
            return faults.Fault(e)
        try:
            route = self._plugin.\
                       create_route(tenant_id, routetable_id,
                                    **request_params)
        except exception.RouteSourceInvalid as invalidsource:
            return faults.Fault(faults.RouteSourceInvalid(invalidsource))
        except exception.RouteDestinationInvalid as invaliddestination:
            return faults.\
                   Fault(faults.RouteDestinationInvalid(invaliddestination))
        except exception.RouteTargetInvalid as invalidtarget:
            return faults.Fault(faults.RouteTargetInvalid(invalidtarget))
        except exception.DuplicateRoute as duplicateroute:
            return faults.Fault(faults.DuplicateRoute(duplicateroute))
        except exception.RoutetableNotFound as notfoundexcp:
            return faults.Fault(faults.RoutetableNotFound(notfoundexcp))
        builder = routes_view.get_view_builder(request)
        result = builder.build(route, route_details=True)['route']
        return self._build_response(request, dict(route=result), 200)

    def delete(self, request, tenant_id, routetable_id, id):
        """ Deletes the route with the specific route ID """
        try:
            self._plugin.delete_route(tenant_id, routetable_id, id)
            return exc.HTTPNoContent()
        except exception.RoutetableNotFound as e:
            return faults.Fault(faults.RoutetableNotFound(e))
        except exception.RouteNotFound as e:
            return faults.Fault(faults.RouteNotFound(e))
