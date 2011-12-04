# vim: tabstop=4 shiftwidth=4 softtabstop=4

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
#    @author Sumit Naiksatam
#


def get_view_builder(req):
    base_url = req.application_url
    return ViewBuilder(base_url)


class ViewBuilder(object):

    def __init__(self, base_url=None):
        """
        :param base_url: url of the root wsgi application
        """
        self.base_url = base_url

    def build(self, route_data, route_details=False):
        """Return a detailed model of a route"""
        if route_details:
            route = self._build_detail(route_data)
        else:
            route = self._build_simple(route_data)
	return route

    def _build_simple(self, route_data):
        """Return a simple model of a route"""
        return dict(route=dict(id=route_data['route_id']))

    def _build_detail(self, route_data):
        """Return a detailed model of a route."""
        return dict(route=dict(id=route_data['route_id'],
                               routetable_id=route_data['routetable_id'],
                               source=route_data['source'],
                               destination=route_data['destination'],
                               target=route_data['target']))
