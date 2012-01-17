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

from quantum.common import exceptions as exc
from quantum.db import api as db

from quantum.plugins.l3.common import constants as const
from quantum.plugins.l3.utils import utils as util
from quantum.plugins.l3.L3BasePlugin import *
from quantum.plugins.l3.utils import iptables

LOG = logging.getLogger(__name__)


class L3LinuxGatewayPlugin(L3BasePlugin):
    """
    L3 Plugin that leverages Linux Bridge and
    IP Tables
    """

    def __init__(self):
        super(L3LinuxGatewayPlugin, self).__init__()
        self.iptables_manager = iptables.IptablesManager()

    def create_subnet(self, tenant_id, cidr, **kwargs):
        """
        Creates a new subnet, and assigns it a symbolic name.
        """
        LOG.debug("L3LinuxGatewayPlugin.create_subnet() called")
        new_subnet = super(L3LinuxGatewayPlugin, self).create_subnet(tenant_id,
                                                              cidr,
                                                              **kwargs)
        self.iptables_manager.subnet_public_drop(cidr)
        return new_subnet

    def delete_subnet(self, tenant_id, subnet_id):
        """
        Deletes the subnet with the specified identifier
        belonging to the specified tenant.
        """
        LOG.debug("L3LinuxGatewayPlugin.delete_subnet() called")
        subnet = super(L3LinuxGatewayPlugin, self).delete_subnet(tenant_id,
                                                          subnet_id)
        self.iptables_manager.subnet_public_accept(subnet[const.CIDR])
        return subnet

    def create_route(self, tenant_id, routetable_id, source, destination,
                     target, **kwargs):
        """
        Creates a new route
        """
        LOG.debug("L3LinuxGatewayPlugin.create_route() called")
        new_route_entry = \
                super(L3LinuxGatewayPlugin, self).create_route(tenant_id,
                                                               routetable_id,
                                                               source,
                                                               destination,
                                                               target,
                                                               **kwargs)
        """
        TODO: For now we assume that the source is a subnet ID,
              we need to later account for CIDR
        """
        subnet_dict = self.get_subnet_details(tenant_id, source)
        if util.strcmp_ignore_case(destination, const.DESTINATION_DEFAULT)\
           and util.strcmp_ignore_case(target, const.TARGET_PUBLIC):
            self.iptables_manager.subnet_public_accept(subnet_dict[const.CIDR])
        return new_route_entry

    def delete_route(self, tenant_id, routetable_id, route_id):
        """
        Deletes the route with the specified id
        """
        LOG.debug("L3LinuxGatewayPlugin.delete_route() called")
        route = self.get_route_details(tenant_id, routetable_id, route_id)
        source = route[const.ROUTE_SOURCE]
        subnet_dict = self.get_subnet_details(tenant_id, source)
        destination = route[const.ROUTE_DESTINATION]
        target = route[const.ROUTE_TARGET]
        if util.strcmp_ignore_case(destination, const.DESTINATION_DEFAULT)\
           and util.strcmp_ignore_case(target, const.TARGET_PUBLIC):
            self.iptables_manager.subnet_public_drop(subnet_dict[const.CIDR])

        route_entry = super(L3LinuxGatewayPlugin, self).delete_route(tenant_id,
                                                              routetable_id,
                                                              route_id)
        return route_entry

    def update_route(self, tenant_id, routetable_id, route_id, **kwargs):
        """
        Updates the attributes of a particular route.
        """
        LOG.debug("L3LinuxRouter.update_route() called")
        route = self.get_route_details(tenant_id, routetable_id, route_id)
        source = route[const.ROUTE_SOURCE]
        subnet_dict = self.get_subnet_details(tenant_id, source)
        destination = route[const.ROUTE_DESTINATION]
        target = route[const.ROUTE_TARGET]
        if util.strcmp_ignore_case(destination, const.DESTINATION_DEFAULT)\
           and util.strcmp_ignore_case(target, const.TARGET_PUBLIC):
            self.iptables_manager.subnet_public_drop(subnet_dict[const.CIDR])

        route = route_get(routetable_id, route_id)
        for key in kwargs.keys():
            route[key] = kwargs[key]
        source = route[const.ROUTE_SOURCE]
        subnet_dict = self.get_subnet_details(tenant_id, source)
        destination = route[const.ROUTE_DESTINATION]
        target = route[const.ROUTE_TARGET]
        if util.strcmp_ignore_case(destination, const.DESTINATION_DEFAULT)\
           and util.strcmp_ignore_case(target, const.TARGET_PUBLIC):
            self.iptables_manager.\
                     subnet_public_accept(subnet_dict[const.CIDR])

        return  super(L3LinuxRouter, self).update_route(tenant_id,
                                                        routetable_id,
                                                        route_id)

    def associate_subnet(self, tenant_id, subnet_id, routetable_id):
        """
        associates a subnet to a routetable
        """
        LOG.debug("L3LinuxRouter.associate_subnet() called")
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

        routetable_id = super(L3LinuxRouter, self).\
                              associate_subnet(tenant_id,
                                               subnet_id,
                                               routetable_id)

    def disassociate_subnet(self, tenant_id, subnet_id):
        """
        disassociates a subnet from a routetable
        """
        LOG.debug("L3LinuxRouter.disassociate_subnet() called")
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

        routetable_id = super(L3LinuxRouter, self).\
                              disassociate_subnet(tenant_id,
                                                  subnet_id,
                                                  routetable_id)
        return routetable_id
