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
from quantum.api.views import targets as targets_view
from quantum.common import exceptions as exception

LOG = logging.getLogger('quantum.api.targets')


class Controller(common.QuantumController):
    """ Targets API controller for Quantum API """

    _route_ops_param_list = [{}]

    _serialization_metadata = {
        "application/xml": {
            "attributes": {
                "route": ["tag", "description"]},
            "plurals": {"targets": "target"}},
    }

    def __init__(self, plugin):
        self._resource_name = 'target'
        super(Controller, self).__init__(plugin)

    def _items(self, request, tenant_id, routetable_id):
        """ Returns a list of targets """
        targets = self._plugin.get_all_targets(tenant_id, routetable_id)
        builder = targets_view.get_view_builder(request)
        result = [builder.build(target)['target']
                  for target in targets]
        return dict(targets=result)

    def get_all_targets(self, request, tenant_id, routetable_id):
        """ Returns a list of targets for this tenant """
        return self._items(request, tenant_id, routetable_id)
