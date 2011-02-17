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

import logging
import unittest
import re

import quantum.tests.unit.l3.testlib_l3targetapi as testlib

from quantum.tests.unit.l3._test_l3api import L3AbstractAPITest
from quantum.wsgi import XMLDeserializer, JSONDeserializer

LOG = logging.getLogger(__name__)

TARGETS = 'targets'
REGEX = "([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})"


class L3TargetAbstractAPITest(L3AbstractAPITest):
    """L3 Target tests class"""
    def _test_list_targets(self, req_format):
        """Testing list targets"""
        LOG.debug("_test_list_targets - req_format:%s - START", req_format)
        content_type = "application/%s" % req_format
        LOG.debug("Creating routetable")
        routetable_req = testlib.new_routetable_request(self.tenant_id,
                                                        req_format,
                                                        None)
        routetable_res = routetable_req.get_response(self.api)
        routetable_id = (re.findall(REGEX, str(routetable_res)))[0]
        content_type = "application/%s" % req_format
        list_target_req = testlib.target_list_request(self.tenant_id,
                                                      routetable_id,
                                                      req_format)
        list_target_res = list_target_req.get_response(self.api)
        self.assertEqual(list_target_res.status_int, 200)
        target_data = self._target_deserializers[content_type].\
                deserialize(list_target_res.body)['body']
        if(req_format == 'xml'):
            self.assertEqual(len(target_data['targets']), 1)
        if(req_format == 'json'):
            self.assertEqual(len(target_data['targets']), 3)
        LOG.debug("_test_list_targets - req_format:%s - END", req_format)

    def setUp(self, api_router_klass, xml_metadata_dict):
        """setUp for the test"""
        super(L3TargetAbstractAPITest, self).setUp(api_router_klass,
                                                   xml_metadata_dict)
        self.tenant_id = "test_tenant"
        self.cidr = "10.0.0.0/24"
        target_xml_deserializer = XMLDeserializer(xml_metadata_dict[TARGETS])
        json_deserializer = JSONDeserializer()
        self._target_deserializers = {
            'application/xml': target_xml_deserializer,
            'application/json': json_deserializer,
        }

    def tearDown(self):
        """Clear the test environment"""
        super(L3TargetAbstractAPITest, self).tearDown()

    def test_list_targets_json(self):
        """Testing list targets with json"""
        self._test_list_targets('json')

    def test_list_targets_xml(self):
        """Testing list targets with xml"""
        self._test_list_targets('xml')
