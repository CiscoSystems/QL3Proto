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
from quantum.plugins.l3.utils import iputils as iputil
from quantum.plugins.l3.utils import utils as util


LOG = logging.getLogger(__name__)


def validate_route_source(tenant_id, routetable_id, source):
    """
    This method returns True if the source is valid in the context of the
    tenant and the routetable. The following checks are performed:
    If the source is a wild card, or,
    If the source is a UUID, is it for a subnet that belongs to this tenant
    and if the subnet is associated with this routetable, or,
    If the source is not a UUID, check if it's a valid CIDR/IPAddress, and,
    If its a valid CIDR/IPAddress, check if it belongs to one of the subnets
    associated with this routetable
    """
    if source == const.STAR_WILD_CARD:
        return True
    try:
        if util.validate_uuid(source):
            for subnet in db.\
                          routetable_get_associated_subnets(routetable_id):
                if subnet.uuid == source:
                    return True
            raise exc.RouteSourceInvalid(source_id=source)
    except exc.RouteSourceInvalid:
        raise
    except Exception as excp:
        if not iputil.validate_cidr(source):
            raise exc.InvalidCIDR(cidr=source)
        else:
            for subnet in db.subnet_list(tenant_id):
                if subnet.cidr == source:
                    return True
            raise exc.RouteSourceInvalid(source_id=source)


def validate_route_destination(tenant_id, routetable_id, destination):
    """
    This method returns True if the destination is valid in the context of the
    tenant and the routetable. The following checks are performed:
    If the destination is the string "default", or,
    If the desintation is the IP address 0.0.0.0, or,
    If the destination is a UUID, is it for a subnet that belongs to this tenant
    If the destination is not a UUID, check if it's a valid CIDR/IPAddress
    """
    if destination.lower() in [const.DESTINATION_DEFAULT,
                               const.DESTINATION_DEFAULT_IP]:
        return True
    try:
        if util.validate_uuid(destination):
            if db.subnet_get_by_tenant(tenant_id, destination):
                return True
            raise exc.RouteDestinationInvalid(destination_id=destination)
    except exc.RouteDestinationInvalid:
        raise
    except Exception as excp:
        if not iputil.validate_cidr(destination):
            raise exc.InvalidCIDR(cidr=destination)
        else:
            return True


def validate_route_target(tenant_id, routetable_id, target):
    """
    This method returns True if the target is found in the list of targets
    """
    return db.target_get(tenant_id, target)
