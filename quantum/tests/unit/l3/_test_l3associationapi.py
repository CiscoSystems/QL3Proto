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

import logging
import re

import quantum.tests.unit.l3.testlib_l3associationapi as testlib

from quantum.tests.unit.l3._test_l3api import L3AbstractAPITest
from quantum.wsgi import XMLDeserializer, JSONDeserializer

LOG = logging.getLogger(__name__)

ASSOCIATIONS = 'associations'

REGEX = "([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})"


class L3AssociationAbstractAPITest(L3AbstractAPITest):
    """L3 Association tests class"""
    def _create_association(self, req_format, subnet_id, routetable_id,
                            custom_req_body=None,
                            expected_res_status=200):
        """Creating a new association"""
        LOG.debug("Creating association")
        content_type = "application/" + req_format
        association_req = testlib.new_association_request(self.tenant_id,
                                                          subnet_id,
                                                          routetable_id,
                                                          req_format,
                                                          custom_req_body)
        association_res = association_req.get_response(self.api)
        self.assertEqual(association_res.status_int, expected_res_status)
        if expected_res_status in (204, 200):
            association_data = self._association_deserializers[content_type].\
                    deserialize(association_res.body)['body']
            return association_data

    def _test_create_association(self, req_format):
        """Test creating a new association"""
        LOG.debug("_test_create_association - req_format:%s - START",
                   req_format)
        content_type = "application/%s" % req_format
        subnet_id = self._create_subnet_id(req_format)
        routetable_id = self._create_routetable_id(req_format)
        association_data = self._create_association(req_format, subnet_id,
                                                    routetable_id)
        self.assertEqual(((re.findall(REGEX, str(association_data)))[0]),
                         routetable_id)
        show_association_req = testlib.show_association_request(self.tenant_id,
                                                                subnet_id,
                                                                req_format)
        show_association_res = show_association_req.get_response(self.api)
        show_association_res_data = self._association_deserializers[\
                content_type].deserialize(show_association_res.body)['body']
        self.assertEqual(show_association_res_data, association_data)
        LOG.debug("_test_create_association - req_format:%s - END", req_format)

    def _test_create_assoc_badreq(self, req_format):
        """Test for a bad request while creating association"""
        LOG.debug("_test_create_assoc_badrequest - req_format:%s - START",
                  req_format)
        bad_body = {'association': {'bad-attribute': 'very-bad'}}
        subnet_id = self._create_subnet_id(req_format)
        routetable_id = self._create_routetable_id(req_format)
        self._create_association(req_format, subnet_id, routetable_id,
                                 custom_req_body=bad_body,
                                 expected_res_status=400)
        self._create_association(req_format, "BAD", "BAD",
                                 custom_req_body=bad_body,
                                 expected_res_status=400)
        LOG.debug("_test_create_association_badrequest - req_format:%s - END",
                  req_format)

    def _test_show_association(self, req_format):
        """Test to show available association"""
        LOG.debug("_test_show_association - req_format:%s - START", req_format)
        content_type = "application/%s" % req_format
        subnet_id = self._create_subnet_id(req_format)
        routetable_id = self._create_routetable_id(req_format)
        create_association_data = self._create_association(req_format,
                                                           subnet_id,
                                                           routetable_id)
        show_association_req = testlib.show_association_request(self.tenant_id,
                                                                subnet_id,
                                                                req_format)
        show_association_res = show_association_req.get_response(self.api)
        self.assertEqual(show_association_res.status_int, 200)
        self.assertEqual(((re.findall(REGEX, str(show_association_res)))[0]),
                         routetable_id)
        show_association_res_data = self._association_deserializers[\
                content_type].deserialize(show_association_res.body)['body']
        self.assertEqual(show_association_res_data, create_association_data)
        LOG.debug("_test_show_association - req_format:%s - END", req_format)

    def _test_show_assoc_not_found(self, req_format):
        """Test to check if no show association found"""
        LOG.debug("_test_show_association_not_found - req_format:%s - START",
                  req_format)
        LOG.debug("Creating subnet")
        show_association_req = testlib.show_association_request(self.tenant_id,
                                                                "BAD",
                                                                req_format)
        show_association_res = show_association_req.get_response(self.api)
        self.assertEqual(show_association_res.status_int, 450)
        LOG.debug("_test_show_association_not_found - req_format:%s - END",
                   req_format)

    def _test_delete_association(self, req_format):
        """Test deleting association"""
        LOG.debug("_test_delete_association - req_format:%s - START",
                   req_format)
        #content_type = "application/%s" % req_format
        subnet_id = self._create_subnet_id(req_format)
        routetable_id = self._create_routetable_id(req_format)
        self._create_association(req_format, subnet_id, routetable_id)
        LOG.debug("Deleting association %s"\
                  " of tenant %s" % (self.tenant_id, subnet_id))
        delete_association_req = testlib.association_delete_request(
                                                    self.tenant_id,
                                                    subnet_id,
                                                    req_format)
        delete_association_res = delete_association_req.get_response(self.api)
        self.assertEqual(delete_association_res.status_int, 200)
        show_association_req = testlib.show_association_request(self.tenant_id,
                                                                subnet_id,
                                                                req_format)
        show_association_res = show_association_req.get_response(self.api)
        if((re.findall(REGEX, str(show_association_res))) == []):
            available_associations = 0
        else:
            available_associations = 1
        self.assertEqual(available_associations, 0)
        LOG.debug("_test_delete_association - req_format:%s - END", req_format)

    def _create_subnet_id(self, req_format):
        """Creating a subnet id for the tests"""
        LOG.debug("_create_subnet_id - START")
        subnet_req = testlib.new_subnet_request(self.tenant_id,
                                                self.cidr, req_format,
                                                None)
        subnet_res = subnet_req.get_response(self.api)
        subnet_id = (re.findall(REGEX, str(subnet_res)))[0]
        return subnet_id
        LOG.debug("_create_subnet_id - END")

    def _create_routetable_id(self, req_format):
        """Creating a routetable_id for the tests"""
        LOG.debug("_create_routetable_id - START")
        routetable_req = testlib.new_routetable_request(self.tenant_id,
                                                        req_format,
                                                        None)
        routetable_res = routetable_req.get_response(self.api)
        routetable_id = (re.findall(REGEX, str(routetable_res)))[0]
        return routetable_id
        LOG.debug("_create_routetable_id - END")

    def _test_unparsable_data(self, req_format):
        """Testing unparsable input data"""
        LOG.debug("_test_unparsable_data - " \
                  " req_format:%s - START", req_format)
        data = "this is not json or xml"
        method = 'PUT'
        content_type = "application/%s" % req_format
        tenant_id = self.tenant_id
        subnet_id = self._create_subnet_id(req_format)
        path = "/tenants/" + str(tenant_id) + "/subnets" \
           "/%(subnet_id)s/association.%(req_format)s" % locals()
        association_req = testlib.create_request(
                path, data, content_type, method)
        association_res = association_req.get_response(self.api)
        self.assertEqual(association_res.status_int, 400)
        LOG.debug("_test_unparsable_data - " \
                  "req_format:%s - END", req_format)

    def setUp(self, api_router_klass, xml_metadata_dict):
        """setUp for the test"""
        super(L3AssociationAbstractAPITest, self).setUp(api_router_klass,
                                                   xml_metadata_dict)
        self.tenant_id = "test_tenant"
        self.cidr = "10.0.0.0/24"
        association_xml_deserializer = XMLDeserializer(
                xml_metadata_dict[ASSOCIATIONS])
        json_deserializer = JSONDeserializer()
        self._association_deserializers = {
            'application/xml': association_xml_deserializer,
            'application/json': json_deserializer,
        }

    def tearDown(self):
        """Clear the test environment"""
        super(L3AssociationAbstractAPITest, self).tearDown()

    def test_create_association_json(self):
        """Test creating a new association with json"""
        self._test_create_association('json')

    def test_create_association_xml(self):
        """Test creating a new association with xml"""
        self._test_create_association('xml')

    def test_create_assoc_badreq_json(self):
        """Test for a bad request while creating association with json"""
        self._test_create_assoc_badreq('json')

    def test_create_assoc_badreq_xml(self):
        """Test for a bad request while creating association with xml"""
        self._test_create_assoc_badreq('xml')

    def test_show_assoc_not_found_json(self):
        """Test to check if no show association found with json"""
        self._test_show_assoc_not_found('json')

    def test_show_assoc_not_found_xml(self):
        """Test to check if no show association found with xml"""
        self._test_show_assoc_not_found('xml')

    def test_show_association_json(self):
        """Test to show available association with json"""
        self._test_show_association('json')

    def test_show_association_xml(self):
        """Test to show available association with xml"""
        self._test_show_association('xml')

    def test_delete_association_json(self):
        """Test deleting association with json"""
        self._test_delete_association('json')

    def test_delete_association_xml(self):
        """Test deleting association with xml"""
        self._test_delete_association('xml')

    def test_unparsable_data_xml(self):
        """Testing unparsable input data with xml"""
        self._test_unparsable_data('xml')

    def test_unparsable_data_json(self):
        """Testing unparsable input data with json"""
        self._test_unparsable_data('json')
