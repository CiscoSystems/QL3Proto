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
# @author: Arvind Somya (asomya@cisco.com), Cisco Systems, Inc.

import ConfigParser
import iplib
import logging
import os
import re

from quantum.common import exceptions as exc
from quantum.common.config import find_config_file
from quantum.db import api as db
from quantum.plugins.quagga.client.zebra.telnet import QuaggaClient


CONF_FILE = find_config_file(
  {"config_file": "etc/quantum/plugins/quagga/QuaggaL3Plugin.ini"},
    None, "QuaggaL3Plugin.ini")

LOG = logging.getLogger('quantum.plugins.QuaggaL3Plugin')


class QuaggaL3Plugin(object):
    def __init__(self, configfile=None):
        # Create quagga client object
        config = ConfigParser.ConfigParser()
        if configfile == None:
            if os.path.exists(CONF_FILE):
                configfile = CONF_FILE
            else:
                configfile = find_config(os.path.abspath(
                        os.path.dirname(__file__)))
        if configfile == None:
            raise Exception("Configuration file \"%s\" doesn't exist" %
              (configfile))
        LOG.debug("Using configuration file: %s" % configfile)
        config.read(configfile)
        LOG.debug("Config: %s" % config)
        self.qclient = QuaggaClient(
                         password = config.get("TELNET", "password"),
                         en_password = config.get("TELNET", "en_password"),
                         host = config.get("TELNET", "host"),
                         port = config.get("TELNET", "port")
                       )

    def _convert_cidr_notation(self, cidr):
        parts = cidr.split("/")
        netmask = iplib.convert_nm(parts[1], notation='dot')

        return (parts[0], netmask)

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
        LOG.debug("QuaggaL3Plugin.get_all_subnets() called")
        subnets = []
        for subnet in db.subnet_list(tenant_id):
            subnet_item = {'subnet_id': str(subnet.uuid),
                           'cidr': subnet.cidr}
            subnets.append(subnet_item)
        return subnets

    def get_subnet_details(self, tenant_id, subnet_id):
        """
        Get details for the specified subnet
        """
        LOG.debug("QuaggaL3Plugin.get_subnet_details() called")
        subnet = self._get_subnet(tenant_id, subnet_id)
        return {'subnet_id': str(subnet.uuid),
                'cidr': subnet.cidr,
                'network_id': subnet.network_id}

    def create_subnet(self, tenant_id, cidr, **kwargs):
        """
        Creates a new subnet, and assigns it a symbolic name.
        """
        LOG.debug("QuaggaL3Plugin.create_subnet() called with, " \
                  "tenant_id: %s, cidr:%s" % (tenant_id, cidr))
        l2network_id = db.network_create(tenant_id, "subnet-" + cidr)['uuid']
        new_subnet = db.subnet_create(tenant_id, cidr, l2network_id)
        # Return uuid for newly created subnetwork as subnet_id.
        return {'subnet_id': new_subnet['uuid']}

    def delete_subnet(self, tenant_id, subnet_id):
        """
        Deletes the subnet with the specified identifier
        belonging to the specified tenant.
        """
        LOG.debug("QuaggaL3Plugin.delete_subnet() called")
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
        LOG.debug("QuaggaL3Plugin.update_subnet() called")
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
        LOG.debug("QuaggaL3Plugin.get_all_routetable() called")
        routetables = []
        for routetable in db.routetable_list(tenant_id):
            routetable_item = {'routetable_id': str(routetable.uuid)}
            routetables.append(routetable_item)
        return routetables

    def get_routetable_details(self, tenant_id, routetable_id):
        """
        retrieved a list of all the routetables
        """
        LOG.debug("QuaggaL3Plugin.get_routetable_details() called")
        routetable = self._get_routetable(tenant_id, routetable_id)
        return {'routetable_id': str(routetable.uuid),
                'label': routetable.label,
                'description': routetable.description}

    def create_routetable(self, tenant_id, **kwargs):
        """
        Creates a new routetable
        """
        LOG.debug("QuaggaL3Plugin.create_routetable() called with, " \
                  "tenant_id: %s" % (tenant_id))
        new_routetable = db.routetable_create(tenant_id, **kwargs)
        # Return uuid for newly created routetablework as routetable_id.
        return {'routetable_id': new_routetable['uuid']}

    def delete_routetable(self, tenant_id, routetable_id):
        """
        Deletes the routetable with the specified identifier
        belonging to the specified tenant.
        """
        LOG.debug("QuaggaL3Plugin.delete_routetable() called")
        routetable = self._get_routetable(tenant_id, routetable_id)

        if routetable:
            # Check for routes in this routetable
            routes = self.get_all_routes(tenant_id, routetable_id)
            if len(routes) > 0:
                raise exc.RoutetableRouteError(routetable_id=routetable_id)

            db.routetable_destroy(routetable_id)
            return routetable
        # Routetable not found
        raise exc.RoutetableNotFound(routetable_id=routetable_id)

    def update_routetable(self, tenant_id, routetable_id, **kwargs):
        """
        Updates the attributes of a particular routetable.
        """
        LOG.debug("QuaggaL3Plugin.update_routetable() called")
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
        LOG.debug("QuaggaL3Plugin.get_all_routes() called")
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
        LOG.debug("QuaggaL3Plugin.create_route() called with, " \
                  "tenant_id: %s routetable_id: %s" % (tenant_id,
                                                       routetable_id))
        new_route = db.route_create(routetable_id, source, destination, target,
                                    **kwargs)
        # Create quagga route
        # Check if either the destination is a subnet id
        new_dest = destination
        net_details = []
        if re.search("[^\/]", destination):
            # Grab the destination cidr
            row = db.subnet_get(destination)
            new_dest = row.cidr

        net_details = self._convert_cidr_notation(new_dest)
        self.qclient.add_static_route(net_details[0], net_details[1], target)

        return {'route_id': new_route['uuid'],
                'routetable_id': new_route['routetable_id'],
                'source': new_route['source'],
                'destination': new_route['destination'],
                'target': new_route['target']}

    def delete_route(self, tenant_id, routetable_id, route_id):
        """
        Deletes the route with the specified id
        """
        LOG.debug("QuaggaL3Plugin.delete_route() called with routetable_id: " \
                  "%s, route_id: %s" % (routetable_id, route_id))
        route = self._get_route(routetable_id, route_id)

        # Delete route
        # Check if either the destination is a subnet id
        new_dest = route.destination
        net_details = []
        if re.search("[^\/]", new_dest):
            # Grab the destination cidr
            row = db.subnet_get(new_dest)
            new_dest = row.cidr

        net_details = self._convert_cidr_notation(new_dest)
        self.qclient.del_static_route(net_details[0], net_details[1], route.target)

        if route:
            db.route_destroy(routetable_id, route_id)
            return route
        # Route not found
        raise exc.RouteNotFound(routetable_id=routetable_id,
                                route_id=route_id)

    def update_route(self, tenant_id, routetable_id, route_id, **kwargs):
        """
        Updates the attributes of a particular route.
        """
        LOG.debug("QuaggaL3Plugin.update_route() called")
        # Deactivate old route
        old_route = db.route_get(routetable_id, route_id)
        old_net_details = self._convert_cidr_notation(old_route['destination'])
        self.qclient.del_static_route(
            old_net_details[0],
            old_net_details[1],
            old_route['target']
        )

        # Compare keys
        for key in ('source','destination','target'):
            if not kwargs[key]:
                kwargs[key] = old_route[key]
        # Update new route
        new_route = db.route_update(routetable_id, route_id, **kwargs)

        # Activate new route
        new_net_details = self._convert_cidr_notation(new_route['destination'])
        self.qclient.add_static_route(
            new_net_details[0], 
            new_net_details[1], 
            new_route['target']
        )

        return {'route_id': new_route['uuid'],
                'routetable_id': new_route['routetable_id'],
                'source': new_route['source'],
                'destination': new_route['destination'],
                'target': new_route['target']}

    def get_route_details(self, tenant_id, routetable_id, route_id):
        """
        retrieves the details of a route
        """
        LOG.debug("QuaggaL3Plugin.get_route_details() called")
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
        LOG.debug("QuaggaL3Plugin.get_all_targets() called")
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
        LOG.debug("QuaggaL3Plugin.get_subnet_association() called")
        return {'routetable_id': db.subnet_get_association(subnet_id)}

    def associate_subnet(self, tenant_id, subnet_id, routetable_id):
        """
        associates a subnet to a routetable
        """
        LOG.debug("QuaggaL3Plugin.associate_subnet() called")
        association = db.subnet_set_association(subnet_id, routetable_id)
        return {'routetable_id': association['routetable_id']}

    def disassociate_subnet(self, tenant_id, subnet_id):
        """
        disassociates a subnet from a routetable
        """
        LOG.debug("QuaggaL3Plugin.disassociate_subnet() called")

        # Check route(s) for this subnet
        routes = db.subnet_get_routes(subnet_id)
        if len(routes) > 0:
            raise exc.SubnetRouteError(subnet_id=subnet_id)
        else:    
            routetable_id = db.subnet_unset_association(subnet_id)
            return {'routetable_id': routetable_id}

    def activate_all_routetables(self, tenant):
        # Get all routetables in this tenant
        routetables = db.routetable_list(tenant)
        # Activate each routetable
        for routetable in routetables:
            self.activate_routetable(tenant, routetable.routetable_id)

    def deactivate_all_routetables(self, tenant):
        # Get all routetables in this tenant
        routetables = db.routetable_list(tenant)
        # Deactivate each routetable
        for routetable in routetables:
            self.deactivate_routetable(tenant, routetable.routetable_id)

    def activate_routetable(self, tenant, routetable_id):
        # Check if this is already the active
        # routetable for this tenant
        curtable = self.get_active_routetable(tenant)
        if curtable == routetable_id:
            return False
        else:
            # Deactivate the current routetable
            self.deactivate_routetable(tenant, curtable)

        # Get all routes in this routetable
        routes = self.get_all_routes(tenant, routetable_id)
        for route in routes:
            net_detail = _convert_cidr_notation(route.destination)
            # Add each route to Quagga
            self.qclient.add_static_route(
                net_detail[0],
                net_detail[1],
                route.target
            )

    def deactivate_routetable(self, tenant, routetable_id):
        # Check if this is the active
        # routetable for this tenant
        curtable = self.get_active_routetable(tenant)
        if curtable != routetable_id:
            # Not the currently active routetable
            return False

        # Get all routes in this routetable
        routes = self.get_all_routes(tenant, routetable_id)
        for route in routes:
            net_detail = _convert_cidr_notation(route.destination)
            # Add each route to Quagga
            self.qclient.del_static_route(
                net_detail[0],
                net_detail[1],
                route.target
            )
