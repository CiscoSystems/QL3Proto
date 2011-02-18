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
#    @author: Sumit Naiksatam, Cisco Systems, Inc.
"""Testing L3 Subnet API"""

import quantum.api.subnets as subnets
import quantum.tests.unit.l3._test_l3subnetapi as test_api

from quantum.common.test_lib import test_config


class L3SubnetAPITestV11(test_api.L3SubnetAbstractAPITest):
    """L3 Subnet API tests class"""

    def assert_subnet(self, **kwargs):
        """Assert Subnet"""
        self.assertEqual({'id': kwargs['id'],
                          'cidr': kwargs['cidr'],
                          'network_id': kwargs['network_id']},
                         kwargs['subnet_data'])

    def assert_subnet_details(self, **kwargs):
        """Assert Subnet details"""
        self.assertEqual({'id': kwargs['id'],
                          'cidr': kwargs['cidr'],
                          'network_id': kwargs['network_id']},
                         kwargs['subnet_data'])

    def setUp(self):
        """setUp for the test"""
        super(L3SubnetAPITestV11, self).setUp('quantum.api.APIRouterV11',
             {test_api.SUBNETS: subnets.ControllerV11._serialization_metadata})
