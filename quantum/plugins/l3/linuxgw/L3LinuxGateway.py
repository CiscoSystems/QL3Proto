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
# @author: Rohit Agarwalla, Cisco Systems, Inc.

import logging

from quantum.db import api as db

from quantum.plugins.l3.common import constants as const
from quantum.plugins.l3.utils import utils as util
from quantum.plugins.l3.utils import iputils as iputil
from quantum.plugins.l3.L3BasePlugin import *
from quantum.plugins.l3.utils import iptables

LOG = logging.getLogger(__name__)

PUBLIC_INTERFACE = "eth1"
TENANT_ID = "t1"


class L3LinuxGatewayPlugin(L3BasePlugin):
    """
    L3 Plugin that leverages Linux Bridge and
    IP Tables
    """

    def __init__(self):
        super(L3LinuxGatewayPlugin, self).__init__()
        self.tenant_id = TENANT_ID
        self.public_interface = PUBLIC_INTERFACE
        self.iptables_manager = iptables.IptablesManager()
        self.restore_iptables()

    def restore_iptables(self):
        """
        Restores the state of the iptables
        """
        LOG.debug("L3LinuxGatewayPlugin.restore_iptables() called")
        self.iptables_manager.initialize()
        """TODO(Rohit): Use enhanced DB methods without tenant_id"""
        subnets = super(L3LinuxGatewayPlugin, self).\
                                  get_all_subnets(self.tenant_id)
        for subnet in subnets:
            subnet_id = subnet['subnet_id']
            subnet_cidr = subnet['cidr']
            self.create_subnet(self.tenant_id, subnet_cidr,\
                               subnet_id=subnet_id)

        routetables = super(L3LinuxGatewayPlugin, self).\
                                      get_all_routetables(self.tenant_id)
        for routetable in routetables:
            routetable_id = routetable['routetable_id']
            routes = super(L3LinuxGatewayPlugin, self).\
                                 get_all_routes(self.tenant_id, routetable_id)
            for route in routes:
                route_id = route['route_id']
                route_source = route['source']
                route_destination = route['destination']
                route_target = route['target']
                self.create_route(self.tenant_id, routetable_id,
                                  route_source, route_destination,
                                  route_target, route_id=route_id)

    def create_subnet(self, tenant_id, cidr, **kwargs):
        """
        Creates a new subnet, and assigns it a symbolic name.
        """
        LOG.debug("L3LinuxGatewayPlugin.create_subnet() called")
        subnet_id = None
        self.iptables_manager.subnet_drop_all(cidr)
        if "subnet_id" in kwargs:
            subnet_id = kwargs['subnet_id']
        if subnet_id is None:
            new_subnet = super(L3LinuxGatewayPlugin, self).\
                                                create_subnet(tenant_id,
                                                              cidr,
                                                              **kwargs)
            return new_subnet

    def delete_subnet(self, tenant_id, subnet_id):
        """
        Deletes the subnet with the specified identifier
        belonging to the specified tenant.
        """
        LOG.debug("L3LinuxGatewayPlugin.delete_subnet() called")
        subnet_dict = self.get_subnet_details(tenant_id, subnet_id)
        self.iptables_manager.subnet_accept_all(subnet_dict[const.CIDR])
        subnet = super(L3LinuxGatewayPlugin, self).delete_subnet(tenant_id,
                                                          subnet_id)
        "TODO(Rohit): Route table cleanup checkup"
        return subnet

    def create_route(self, tenant_id, routetable_id, source, destination,
                     target, **kwargs):
        """
        Creates a new route
        """
        LOG.debug("L3LinuxGatewayPlugin.create_route() called")
        route_id = None
        if "route_id" in kwargs:
            route_id = kwargs["route_id"]
        if route_id is None:
            new_route_entry = \
                super(L3LinuxGatewayPlugin, self).create_route(tenant_id,
                                                               routetable_id,
                                                               source,
                                                               destination,
                                                               target,
                                                               **kwargs)
        if iputil.validate_cidr(source):
            source_cidr = source
        else:
            source_subnet_dict = self.get_subnet_details(tenant_id, source)
            source_cidr = source_subnet_dict[const.CIDR]
        # TODO (Sumit): Also check for const.DESTINATION_DEFAULT_IP
        if util.strcmp_ignore_case(destination, const.DESTINATION_DEFAULT)\
           and util.strcmp_ignore_case(target, const.TARGET_PUBLIC):
            self.iptables_manager.\
                    subnet_public_accept(source_cidr, self.public_interface)
        if util.strcmp_ignore_case(target, const.TARGET_PRIVATE):
            if iputil.validate_cidr(destination):
                destination_cidr = destination
            else:
                destination_subnet_dict = self.get_subnet_details(tenant_id,
                                                                  destination)
                destination_cidr = destination_subnet_dict[const.CIDR]
            self.iptables_manager.\
                 inter_subnet_accept(source_cidr, destination_cidr)
        return new_route_entry

    def delete_route(self, tenant_id, routetable_id, route_id):
        """
        Deletes the route with the specified id
        """
        LOG.debug("L3LinuxGatewayPlugin.delete_route() called")
        route = self.get_route_details(tenant_id, routetable_id, route_id)
        source = route[const.ROUTE_SOURCE]
        if iputil.validate_cidr(source):
            source_cidr = source
        else:
            source_subnet_dict = self.get_subnet_details(tenant_id, source)
            source_cidr = source_subnet_dict[const.CIDR]
        destination = route[const.ROUTE_DESTINATION]
        target = route[const.ROUTE_TARGET]
        # TODO (Sumit): Also check for const.DESTINATION_DEFAULT_IP
        if util.strcmp_ignore_case(destination, const.DESTINATION_DEFAULT)\
           and util.strcmp_ignore_case(target, const.TARGET_PUBLIC):
            self.iptables_manager.\
                    subnet_public_drop(source_cidr, self.public_interface)
        if util.strcmp_ignore_case(target, const.TARGET_PRIVATE):
            if iputil.validate_cidr(destination):
                destination_cidr = destination
            else:
                destination_subnet_dict = self.get_subnet_details(tenant_id,
                                                                  destination)
                destination_cidr = destination_subnet_dict[const.CIDR]
            self.iptables_manager.\
                 inter_subnet_drop(source_cidr, destination_cidr)

        route_entry = super(L3LinuxGatewayPlugin, self).delete_route(tenant_id,
                                                              routetable_id,
                                                              route_id)
        return route_entry

    def associate_subnet(self, tenant_id, subnet_id, routetable_id):
        """
        associates a subnet to a routetable
        """
        LOG.debug("L3LinuxGateway.associate_subnet() called")
        """
        routes = self.get_all_routes(tenant_id, routetable_id)
        for route in routes:
            source = route[const.ROUTE_SOURCE]
            subnet_dict = self.get_subnet_details(tenant_id, source)
            destination = route[const.ROUTE_DESTINATION]
            target = route[const.ROUTE_TARGET]
            if util.strcmp_ignore_case(destination, const.DESTINATION_DEFAULT)\
              and util.strcmp_ignore_case(target, const.TARGET_PUBLIC):
                self.iptables_manager.\
                     subnet_public_accept(subnet_dict[const.CIDR])

        """
        return super(L3LinuxGatewayPlugin, self).\
                              associate_subnet(tenant_id,
                                               subnet_id,
                                               routetable_id)

    def disassociate_subnet(self, tenant_id, subnet_id):
        """
        disassociates a subnet from a routetable
        """
        LOG.debug("L3LinuxRouter.disassociate_subnet() called")
        """
        routes = self.get_all_routes(tenant_id, routetable_id)
        for route in routes:
            source = route[const.ROUTE_SOURCE]
            subnet_dict = self.get_subnet_details(tenant_id, source)
            destination = route[const.ROUTE_DESTINATION]
            target = route[const.ROUTE_TARGET]
            if util.strcmp_ignore_case(destination, const.DESTINATION_DEFAULT)\
              and util.strcmp_ignore_case(target, const.TARGET_PUBLIC):
                self.iptables_manager.\
                     subnet_public_drop(subnet_dict[const.CIDR])
        """

        return super(L3LinuxGatewayPlugin, self).\
                              disassociate_subnet(tenant_id,
                                                  subnet_id,
                                                  routetable_id)
