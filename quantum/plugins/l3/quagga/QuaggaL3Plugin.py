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

from quantum.plugins.l3.common import constants as const
from quantum.plugins.l3.utils import utils as util
from quantum.plugins.l3.L3BasePlugin import *
from quantum.plugins.l3.utils import iptables

from quantum.plugins.l3.quagga.client.zebra.telnet import QuaggaClient

CONF_FILE = find_config_file(
  {"config_file": "etc/quantum/plugins/quagga/QuaggaL3Plugin.ini"},
    None, "QuaggaL3Plugin.ini")

LOG = logging.getLogger('quantum.plugins.QuaggaL3Plugin')


class QuaggaL3Plugin(L3BasePlugin):
    def __init__(self, configfile=None):
        super(QuaggaL3Plugin, self).__init__()
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
        self.config = config
        LOG.debug("Config: %s" % config)
        self.qclient = QuaggaClient(
                         password = config.get("TELNET", "password"),
                         en_password = config.get("TELNET", "en_password"),
                         host = config.get("TELNET", "host"),
                         port = config.get("TELNET", "port")
                       )
        self.iptables_manager = iptables.IptablesManager()
        #self.restore_iptables()


    def restore_iptables(self):
        """
        Restores the state of the iptables
        """
        LOG.debug("QuaggaL3Plugin.restore_iptables() called")
        self.iptables_manager.initialize()
        """TODO(Rohit): Use enhanced DB methods without tenant_id"""
        subnets = super(QuaggaL3Plugin, self).\
                                  get_all_subnets(self.tenant_id)
        for subnet in subnets:
            subnet_id = subnet['subnet_id']
            subnet_cidr = subnet['cidr']
            self.create_subnet(self.tenant_id, subnet_cidr,\
                               subnet_id=subnet_id)

        routetables = super(QuaggaL3Plugin, self).\
                                      get_all_routetables(self.tenant_id)
        for routetable in routetables:
            routetable_id = routetable['routetable_id']
            routes = super(QuaggaL3Plugin, self).\
                                 get_all_routes(self.tenant_id, routetable_id)
            for route in routes:
                route_id = route['route_id']
                route_source = route['source']
                route_destination = route['destination']
                route_target = route['target']
                self.create_route(self.tenant_id, routetable_id,
                                  route_source, route_destination,
                                  route_target, route_id=route_id)


    def _convert_cidr_notation(self, cidr):
        parts = cidr.split("/")
        netmask = iplib.convert_nm(parts[1], notation='dot')

        return (parts[0], netmask)

    
    def create_subnet(self, tenant_id, cidr, **kwargs):
        """
        Creates a new subnet, and assigns it a symbolic name.
        """
        LOG.debug("QuaggaL3Plugin.create_subnet() called")
        subnet_id = None
        self.iptables_manager.subnet_drop_all(cidr)
        if "subnet_id" in kwargs:
            subnet_id = kwargs['subnet_id']
        if subnet_id is None:
            new_subnet = super(QuaggaL3Plugin, self).\
                                                create_subnet(tenant_id,
                                                              cidr,
                                                              **kwargs)
            return new_subnet


    def delete_subnet(self, tenant_id, subnet_id):
        """
        Deletes the subnet with the specified identifier
        belonging to the specified tenant.
        """
        LOG.debug("QuaggaL3Plugin.delete_subnet() called")
        subnet_dict = self.get_subnet_details(tenant_id, subnet_id)
        self.iptables_manager.subnet_accept_all(subnet_dict[const.CIDR])
        subnet = super(QuaggaL3Plugin, self).delete_subnet(tenant_id,
                                                          subnet_id)
        "TODO(Rohit): Route table cleanup checkup"
        return subnet


    def create_route(self, tenant_id, routetable_id, source, destination,
                     target, **kwargs):
        """
        Creates a new route
        """
        LOG.debug("QuaggaL3Plugin.create_route() called")
        source_subnet_dict = self.get_subnet_details(tenant_id, source)

        if util.strcmp_ignore_case(destination, const.DESTINATION_DEFAULT):
            LOG.debug("Creating PUBLIC route")
            self.iptables_manager.\
                    subnet_public_accept(source_subnet_dict[const.CIDR], target,
                                         self.config.get("INTERFACE","public"))
            LOG.debug("Added IPTABLES rule")
            source_details =  self._convert_cidr_notation(
                                source_subnet_dict[const.CIDR]
                              )
            self.qclient.add_static_route(
                source_details[0], 
                source_details[1], 
                target
            )
            LOG.debug("Created Quagga route")
        else:
            destination_subnet_dict = \
                    self.get_subnet_details(tenant_id, destination)
            self.iptables_manager.\
                 inter_subnet_accept(source_subnet_dict[const.CIDR],
                                 destination_subnet_dict[const.CIDR])
            dest_details = self._convert_cidr_notation(
                           destination_subnet_dict[const.CIDR]
                       )
            self.qclient.add_static_route(dest_details[0], dest_details[1], target)

        route_id = None
        if "route_id" in kwargs:
            route_id = kwargs["route_id"]
        if route_id is None:
            new_route_entry = \
                super(QuaggaL3Plugin, self).create_route(tenant_id,
                                                         routetable_id,
                                                         source,
                                                         destination,
                                                         target,
                                                         **kwargs)
            return new_route_entry


    def delete_route(self, tenant_id, routetable_id, route_id):
        """
        Deletes the route with the specified id
        """
        LOG.debug("QuaggaL3Plugin.delete_route() called")
        route = self.get_route_details(tenant_id, routetable_id, route_id)

        source = route[const.ROUTE_SOURCE]
        source_subnet_dict = self.get_subnet_details(tenant_id, source)
        destination = route[const.ROUTE_DESTINATION]
        target = route[const.ROUTE_TARGET]

        if destination == 'default':
           self.iptables_manager.\
                subnet_public_drop(source_subnet_dict[const.CIDR],
                                   target)
        else:
            destination_subnet_dict = \
                    self.get_subnet_details(tenant_id, destination)
            self.iptables_manager.\
                inter_subnet_drop(source_subnet_dict[const.CIDR],
                                  destination_subnet_dict[const.CIDR])

        net_details = self._convert_cidr_notation(
                        destination_subnet_dict[const.CIDR]
                      )
        self.qclient.del_static_route(net_details[0], net_details[1], route.target)

        route_entry = super(QuaggaL3Plugin, self).delete_route(tenant_id,
                                                              routetable_id,
                                                              route_id)
        return route_entry


    """
    ** Not implemented
    """
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

    """
    ** These methods are not implemented currently.
    ** They deal with activating/deactivating routetables
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
    """
