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

from quantum.plugins.l3.L3BasePlugin import *

LOG = logging.getLogger(__name__)


class L3LinuxGatewayPlugin(L3BasePlugin):
    """
    L3 Plugin that leverages Linux Bridge and
    IP Tables
    """

    def __init__(self):
        super(L3LinuxGatewayPlugin, self).__init__()

    def create_route(self, tenant_id, routetable_id, source, destination,
                     target, **kwargs):
        """
        Creates a new route
        """
        LOG.debug("L3BasePlugin.create_route() called with, " \
                  "tenant_id: %s routetable_id: %s" % (tenant_id,
                                                       routetable_id))
        new_route = db.route_create(routetable_id, source, destination, target,
                                    **kwargs)
        return {'route_id': new_route['uuid'],
                'routetable_id': new_route['routetable_id'],
                'source': new_route['source'],
                'destination': new_route['destination'],
                'target': new_route['target']}
