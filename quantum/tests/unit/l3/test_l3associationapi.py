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
"""Testing L3 Association API"""

import quantum.api.l3.associations as associations
import quantum.tests.unit.l3._test_l3associationapi as test_api


class L3AssociationAPITestV11(test_api.L3AssociationAbstractAPITest):
    """L3 Association tests class"""

    def assert_association(self, **kwargs):
        """Assert Association"""
        self.assertEqual({'routetable_id': kwargs['routetable_id']},
                         kwargs['association_data'])

    def setUp(self, api_router_klass=None, xml_metadata_dict=None):
        """setUp for the test"""
        super(L3AssociationAPITestV11, self).setUp('quantum.api.APIRouterV11',
             {test_api.ASSOCIATIONS: \
              associations.ControllerV11._serialization_metadata})
