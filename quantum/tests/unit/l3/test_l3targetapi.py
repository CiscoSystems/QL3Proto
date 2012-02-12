# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011, Cisco Systems, Inc.
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
#    @author: Atul Gaikwad, Cisco Systems, Inc.
"""Testing L3 Target API"""

import quantum.api.l3.targets as targets
import quantum.tests.unit.l3._test_l3targetapi as test_api


class L3TargetAPITestV11(test_api.L3TargetAbstractAPITest):
    """L3 Target tests class"""

    def assert_target(self, **kwargs):
        """Assert Target"""
        self.assertEqual({'target': kwargs['target'],
                          'description': kwargs['description']},
                         kwargs['target_data'])

    def setUp(self, api_router_klass=None, xml_metadata_dict=None):
        """setUp for the test"""
        super(L3TargetAPITestV11, self).setUp('quantum.api.APIRouterV11',
             {test_api.TARGETS: targets.ControllerV11._serialization_metadata})
