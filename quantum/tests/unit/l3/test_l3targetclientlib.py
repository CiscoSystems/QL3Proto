# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2011 Cisco Systems
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
#    @author: Atul Gaikwad, Cisco Systems
"""Testing L3 Target CLI"""

import logging
import unittest
import re

from quantum.tests.unit.l3.test_l3clientlib import L3CLIAPITest

LOG = logging.getLogger(__name__)

TENANT_1 = 'tenant1'
TENANT_2 = 'tenant2'


class L3TargetCLIAPITest(L3CLIAPITest):
    """L3 Target tests class"""
    def _test_list_targets(self, tenant=TENANT_1,
                           format='json', status=200):
        """Test to list available target"""
        LOG.debug("_test_list_target - tenant:%s "\
                  "- format:%s - START", format, tenant)
        self._assert_sanity(self.client.list_available_targets,
                            status,
                            "GET",
                            "routetables/001/targets",
                            data=["001"],
                            params={'tenant': tenant,
                                    'format': format})
        LOG.debug("_test_list_targets - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def test_list_targets_json(self):
        """Test to list available target with json"""
        self._test_list_targets(format='json')

    def test_list_targets_xml(self):
        """Test to list available target with xml"""
        self._test_list_targets(format='xml')

    def test_list_targets_alt_tenant(self):
        """Test to list available target with alternate tenant"""
        self._test_list_targets(tenant=TENANT_2)

    def test_list_targets_error_470(self):
        """Test to list available target for error 470"""
        self._test_list_targets(status=470)

    def test_list_targets_error_401(self):
        """Test to list available target for error 401"""
        self._test_list_targets(status=401)
