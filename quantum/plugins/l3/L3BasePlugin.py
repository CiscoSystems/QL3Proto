# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011, Cisco Systems, Inc.
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
# @author: Sumit Naiksatam, Cisco Systems, Inc.

import logging

from quantum.common import exceptions as exc
from quantum.plugins.l3.common import constants as const
from quantum.plugins.l3.db import l3network_db as db
from quantum.plugins.l3.utils import l3utils as l3util
from quantum.plugins.l3.utils import iputils as iputil
from quantum.plugins.l3.utils import utils as util
from quantum.quantum_l3plugin_base import QuantumL3PluginBase


LOG = logging.getLogger('quantum.plugins.L3BasePlugin')


class L3BasePlugin(QuantumL3PluginBase):
    """
    L3BasePlugin is a base class for L3 plugins
    """

    def __init__(self):
        db.initialize()
        try:
            db.target_create("Private", None, description="System")
        except:
            pass
        try:
            db.target_create("Public", None, description="System")
        except:
            pass
        try:
            db.target_create("VPN", None, description="System")
        except:
            pass
        self.l2_plugin_ref = None

    def _get_subnet(self, tenant_id, subnet_id):
        try:
            subnet = db.subnet_get(subnet_id)
        except:
            raise exc.SubnetNotFound(subnet_id=subnet_id)
        return subnet

    def get_all_subnets(self, tenant_id):
        """
        Returns a dictionary containing all
        <subnet_uuid, cidr> for the specified tenant.
        """
        LOG.debug("L3BasePlugin.get_all_subnet() called")
        subnets = []
        for subnet in db.subnet_list(tenant_id):
            subnet_item = {'subnet_id': str(subnet.uuid),
                           'cidr': subnet.cidr,
                           'network_id': subnet.network_id}
            subnets.append(subnet_item)
        return subnets

    def get_subnet_details(self, tenant_id, subnet_id):
        """
        retrieved a list of all the subnets
        """
        LOG.debug("L3BasePlugin.get_subnet_details() called")
        subnet = self._get_subnet(tenant_id, subnet_id)
        return {'subnet_id': str(subnet.uuid),
                'cidr': subnet.cidr,
                'network_id': subnet.network_id}

    def create_subnet(self, tenant_id, cidr, **kwargs):
        """
        Creates a new subnet, and assigns it a symbolic name.
        """
        LOG.debug("L3BasePlugin.create_subnet() called with, " \
                  "tenant_id: %s, cidr:%s" % (tenant_id, cidr))
        if not iputil.validate_subnet_cidr(cidr):
            raise exc.InvalidCIDR(cidr=cidr)
        if not self.l2_plugin_ref:
            self.l2_plugin_ref = util.get_l2_plugin_reference()
        """
        TODO (Sumit): Check first if the network_id is provided in kwargs
        """
        l2network_id = self.l2_plugin_ref.\
                create_network(tenant_id, "subnet-" + cidr)['net-id']
        new_subnet = db.subnet_create(tenant_id, cidr, l2network_id)
        # Return uuid for newly created subnetwork as subnet_id.
        return {'subnet_id': new_subnet['uuid']}

    def delete_subnet(self, tenant_id, subnet_id):
        """
        Deletes the subnet with the specified identifier
        belonging to the specified tenant.
        """
        LOG.debug("L3BasePlugin.delete_subnet() called")
        subnet = self._get_subnet(tenant_id, subnet_id)
        if subnet:
            db.subnet_destroy(subnet_id)
            return subnet
        # Subnet not found
        raise exc.SubnetNotFound(subnet_id=subnet_id)

    def update_subnet(self, tenant_id, subnet_id, **kwargs):
        """
        Updates the attributes of a particular subnet.
        """
        LOG.debug("L3BasePlugin.update_subnet() called")
        if kwargs.has_key('cidr'):
            if not iputil.validate_subnet_cidr(kwargs['cidr']):
                raise exc.InvalidCIDR(cidr=kwargs['cidr'])
        subnet = db.subnet_update(subnet_id, tenant_id, **kwargs)
        return {'subnet_id': str(subnet.uuid),
                'cidr': subnet.cidr,
                'network_id': subnet.network_id}

    def _get_routetable(self, tenant_id, routetable_id):
        try:
            routetable = db.routetable_get(routetable_id)
        except:
            raise exc.RoutetableNotFound(routetable_id=routetable_id)
        return routetable

    def get_all_routetables(self, tenant_id):
        """
        Returns a dictionary containing all
        <routetable_id> for the specified tenant.
        """
        LOG.debug("L3BasePlugin.get_all_routetable() called")
        routetables = []
        for routetable in db.routetable_list(tenant_id):
            routetable_item = {'routetable_id': str(routetable.uuid)}
            routetables.append(routetable_item)
        return routetables

    def get_routetable_details(self, tenant_id, routetable_id):
        """
        retrieved a list of all the routetables
        """
        LOG.debug("L3BasePlugin.get_routetable_details() called")
        routetable = self._get_routetable(tenant_id, routetable_id)
        return {'routetable_id': str(routetable.uuid),
                'label': routetable.label,
                'description': routetable.description}

    def create_routetable(self, tenant_id, **kwargs):
        """
        Creates a new routetable
        """
        LOG.debug("L3BasePlugin.create_routetable() called with, " \
                  "tenant_id: %s" % (tenant_id))
        new_routetable = db.routetable_create(tenant_id, **kwargs)
        # Return uuid for newly created routetablework as routetable_id.
        return {'routetable_id': new_routetable['uuid']}

    def delete_routetable(self, tenant_id, routetable_id):
        """
        Deletes the routetable with the specified identifier
        belonging to the specified tenant.
        """
        LOG.debug("L3BasePlugin.delete_routetable() called")
        routetable = self._get_routetable(tenant_id, routetable_id)
        if routetable:
            db.routetable_destroy(routetable_id)
            return routetable
        # Routetable not found
        raise exc.RoutetableNotFound(routetable_id=routetable_id)

    def update_routetable(self, tenant_id, routetable_id, **kwargs):
        """
        Updates the attributes of a particular routetable.
        """
        LOG.debug("L3BasePlugin.update_routetable() called")
        routetable = db.routetable_update(routetable_id, tenant_id, **kwargs)
        return {'routetable_id': str(routetable.uuid),
                'label': routetable.label,
                'description': routetable.description}

    def _get_route(self, routetable_id, route_id):
        try:
            route = db.route_get(routetable_id, route_id)
        except:
            raise exc.RouteNotFound(routetable_id=routetable_id,
                                    route_id=route_id)
        return route

    def get_all_routes(self, tenant_id, routetable_id):
        """
        Returns a dictionary containing all
        <route_id, routetable_id, source, destination, target>
        for the specified routetable.
        """
        LOG.debug("L3BasePlugin.get_all_routes() called")
        routes = []
        for route in db.route_list(routetable_id):
            route_item = {'route_id': route['uuid'],
                          'routetable_id': route.routetable_id,
                          'source': route.source,
                          'destination': route.destination,
                          'target': route.target}
            routes.append(route_item)
        return routes

    def create_route(self, tenant_id, routetable_id, source, destination,
                     target, **kwargs):
        """
        Creates a new route
        """
        LOG.debug("L3BasePlugin.create_route() called with, " \
                  "tenant_id: %s routetable_id: %s" % (tenant_id,
                                                       routetable_id))
        target = target.lower()
        l3util.validate_route_source(tenant_id, routetable_id, source)
        l3util.validate_route_destination(tenant_id, routetable_id, destination)
        #l3util.validate_route_target(tenant_id, routetable_id, target)
        new_route = db.route_create(routetable_id, source, destination, target,
                                    **kwargs)
        return {'route_id': new_route['uuid'],
                'routetable_id': new_route['routetable_id'],
                'source': new_route['source'],
                'destination': new_route['destination'],
                'target': new_route['target']}

    def delete_route(self, tenant_id, routetable_id, route_id):
        """
        Deletes the route with the specified id
        """
        LOG.debug("L3BasePlugin.delete_route() called with routetable_id: " \
                  "%s, route_id: %s" % (routetable_id, route_id))
        route = self._get_route(routetable_id, route_id)
        if route:
            db.route_destroy(routetable_id, route_id)
            return route
        # Route not found
        raise exc.RouteNotFound(routetable_id=routetable_id,
                                route_id=route_id)

    def get_route_details(self, tenant_id, routetable_id, route_id):
        """
        retrieves the details of a route
        """
        LOG.debug("L3BasePlugin.get_route_details() called")
        route = self._get_route(routetable_id, route_id)
        return {'route_id': route['uuid'],
                'routetable_id': route['routetable_id'],
                'source': route['source'],
                'destination': route['destination'],
                'target': route['target']}

    def get_all_targets(self, tenant_id, routetable_id):
        """
        Returns a dictionary of all targets in the format
        <tag, tenant_id, description>
        """
        LOG.debug("L3BasePlugin.get_all_targets() called")
        targets = []
        for target in db.target_list(tenant_id):
            target_item = {'target': target['tag'],
                          'description': target['description']}
            targets.append(target_item)
        return targets

    def get_subnet_association(self, tenant_id, subnet_id):
        """
        retrieves the routetable associated with a subnet
        """
        LOG.debug("L3BasePlugin.get_subnet_association() called")
        return {'routetable_id': db.subnet_get_association(subnet_id)}

    def associate_subnet(self, tenant_id, subnet_id, routetable_id):
        """
        associates a subnet to a routetable
        """
        LOG.debug("L3BasePlugin.associate_subnet() called")
        association = db.subnet_set_association(subnet_id, routetable_id)
        return {'routetable_id': association['routetable_id']}

    def disassociate_subnet(self, tenant_id, subnet_id):
        """
        disassociates a subnet from a routetable
        """
        LOG.debug("L3BasePlugin.disassociate_subnet() called")
        routetable_id = db.subnet_unset_association(subnet_id)
        return {'routetable_id': routetable_id}
