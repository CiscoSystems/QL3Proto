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
#    @author: Shubhangi Satras, Cisco Systems, Inc.
""" Class for Routetable API testing """

import quantum.api.routetables as routetables
import quantum.tests.unit.l3._test_l3routetableapi as test_api


class L3RoutetableAPITestV11(test_api.L3RoutetableAbstractAPITest):
    """ This class is for testing the routetable API"""

    def assert_routetable(self, **kwargs):
        """This tests the assertion of routtetable"""
        self.assertEqual({'id': kwargs['id'],
                          'label': kwargs['label'],
                          'description': kwargs['description']},
                         kwargs['routetable_data'])

    def assert_routetable_details(self, **kwargs):
        """This tests the assertion of routtetable in detail"""
        self.assertEqual({'id': kwargs['id'],
                          'label': kwargs['label'],
                          'description': kwargs['description']},
                         kwargs['routetable_data'])

    def setUp(self, api_router_klass=None, xml_metadata_dict=None):
        """This is setUp for setting the parameters before use"""
        super(L3RoutetableAPITestV11, self).setUp('quantum.api.APIRouterV11',
             {test_api.ROUTETABLES: routetables.ControllerV11.\
              _serialization_metadata})
