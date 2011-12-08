# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010-2011 ????
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

import logging
import unittest


import quantum.tests.unit.testlib_l3api as testlib

from quantum import api as server
from quantum.common.serializer import Serializer
from quantum.common.test_lib import test_config
from quantum.db import api as db

LOG = logging.getLogger('quantum.tests.test_l3api')


class L3APITest(unittest.TestCase):

    def _test_unparsable_data(self, format):
        LOG.debug("_test_unparsable_data - " \
                  " format:%s - START", format)

        data = "this is not json or xml"
        method = 'POST'
        content_type = "application/%s" % format
        tenant_id = self.tenant_id
        path = "/tenants/%(tenant_id)s/networks.%(format)s" % locals()
        network_req = testlib.create_request(path, data, content_type, method)
        network_res = network_req.get_response(self.api)
        self.assertEqual(network_res.status_int, 400)

        LOG.debug("_test_unparsable_data - " \
                  "format:%s - END", format)

    def _create_subnet(self, format, cidr=None, custom_req_body=None,
                        expected_res_status=200):
        LOG.debug("Creating subnet")
        content_type = "application/" + format
        if not cidr:
            cidr = self.cidr
        subnet_req = testlib.new_subnet_request(self.tenant_id,
                                                  cidr, format,
                                                  custom_req_body)
        subnet_res = subnet_req.get_response(self.api)
        self.assertEqual(subnet_res.status_int, expected_res_status)
        if expected_res_status in (200, 202):
            subnet_data = Serializer().deserialize(subnet_res.body,
                                                    content_type)
            return subnet_data['subnet']['id']

    def _test_create_subnet(self, format):
        LOG.debug("_test_create_subnet - format:%s - START", format)
        content_type = "application/%s" % format
        subnet_id = self._create_subnet(format)
        show_subnet_req = testlib.show_subnet_request(self.tenant_id,
                                                        subnet_id,
                                                        format)
        show_subnet_res = show_subnet_req.get_response(self.api)
        self.assertEqual(show_subnet_res.status_int, 200)
        subnet_data = Serializer().deserialize(show_subnet_res.body,
                                                content_type)
        self.assertEqual(subnet_id, subnet_data['subnet']['id'])
        LOG.debug("_test_create_subnet - format:%s - END", format)

    def _test_create_subnet_badrequest(self, format):
        LOG.debug("_test_create_subnet_badrequest - format:%s - START",
                  format)
        bad_body = {'subnet': {'bad-attribute': 'very-bad'}}
        self._create_subnet(format, custom_req_body=bad_body,
                             expected_res_status=400)
        LOG.debug("_test_create_subnet_badrequest - format:%s - END",
                  format)

    def _test_list_subnets(self, format):
        LOG.debug("_test_list_subnets - format:%s - START", format)
        content_type = "application/%s" % format
        self._create_subnet(format, "10.0.1.0/24")
        self._create_subnet(format, "10.0.2.0/24")
        list_subnet_req = testlib.subnet_list_request(self.tenant_id,
                                                        format)
        list_subnet_res = list_subnet_req.get_response(self.api)
        self.assertEqual(list_subnet_res.status_int, 200)
        subnet_data = self._subnet_serializer.deserialize(
                           list_subnet_res.body, content_type)
        # Check subnet count: should return 2
        self.assertEqual(len(subnet_data['subnets']), 2)
        LOG.debug("_test_list_subnets - format:%s - END", format)

    def _test_list_subnets_detail(self, format):
        LOG.debug("_test_list_subnets_detail - format:%s - START", format)
        content_type = "application/%s" % format
        self._create_subnet(format, "10.0.1.0/24")
        self._create_subnet(format, "10.0.2.0/24")
        list_subnet_req = testlib.subnet_list_detail_request(self.tenant_id,
                                                               format)
        list_subnet_res = list_subnet_req.get_response(self.api)
        self.assertEqual(list_subnet_res.status_int, 200)
        subnet_data = self._subnet_serializer.deserialize(
                           list_subnet_res.body, content_type)
        # Check subnet count: should return 2
        self.assertEqual(len(subnet_data['subnets']), 2)
        # Check contents - id & cidr for each subnet
        for subnet in subnet_data['subnets']:
            self.assertTrue('id' in subnet and 'cidr' in subnet)
            self.assertTrue(subnet['id'] and subnet['cidr'])
        LOG.debug("_test_list_subnets_detail - format:%s - END", format)

    def _test_show_subnet(self, format):
        LOG.debug("_test_show_subnet - format:%s - START", format)
        content_type = "application/%s" % format
        subnet_id = self._create_subnet(format)
        show_subnet_req = testlib.show_subnet_request(self.tenant_id,
                                                        subnet_id,
                                                        format)
        show_subnet_res = show_subnet_req.get_response(self.api)
        self.assertEqual(show_subnet_res.status_int, 200)
        subnet_data = self._subnet_serializer.deserialize(
                           show_subnet_res.body, content_type)['subnet']
        #TODO (Sumit): The assertion for the network_id needs to be different
        self.assertEqual({'id': subnet_id,
                          'cidr': self.cidr,
                          'network_id': subnet_data['network_id']},
                          subnet_data)
        LOG.debug("_test_show_subnet - format:%s - END", format)

    def _test_show_subnet_detail(self, format):
        LOG.debug("_test_show_subnet_detail - format:%s - START", format)
        content_type = "application/%s" % format
        # Create a subnet
        subnet_id = self._create_subnet(format)
        # TODO (Sumit): netowork_id needs to be added as an arg here
        show_subnet_req = testlib.show_subnet_detail_request(
                                    self.tenant_id, subnet_id, format)
        show_subnet_res = show_subnet_req.get_response(self.api)
        self.assertEqual(show_subnet_res.status_int, 200)
        subnet_data = self._subnet_serializer.deserialize(
                           show_subnet_res.body, content_type)['subnet']
        #TODO (Sumit): The assertion for the network_id needs to be different
        self.assertEqual({'id': subnet_id,
                          'cidr': self.cidr,
                          'network_id': subnet_data['network_id']},
                         subnet_data)
        LOG.debug("_test_show_subnet_detail - format:%s - END", format)

    def _test_show_subnet_not_found(self, format):
        LOG.debug("_test_show_subnet_not_found - format:%s - START", format)
        show_subnet_req = testlib.show_subnet_request(self.tenant_id,
                                                        "A_BAD_ID",
                                                        format)
        show_subnet_res = show_subnet_req.get_response(self.api)
        self.assertEqual(show_subnet_res.status_int, 450)
        LOG.debug("_test_show_subnet_not_found - format:%s - END", format)

    def _test_update_subnet(self, format):
        LOG.debug("_test_update_subnet - format:%s - START", format)
        content_type = "application/%s" % format
        new_cidr = '10.0.3.0/24'
        subnet_id = self._create_subnet(format)
        update_subnet_req = testlib.update_subnet_request(self.tenant_id,
                                                            subnet_id,
                                                            new_cidr,
                                                            format)
        update_subnet_res = update_subnet_req.get_response(self.api)
        self.assertEqual(update_subnet_res.status_int, 204)
        show_subnet_req = testlib.show_subnet_request(self.tenant_id,
                                                        subnet_id,
                                                        format)
        show_subnet_res = show_subnet_req.get_response(self.api)
        self.assertEqual(show_subnet_res.status_int, 200)
        subnet_data = self._subnet_serializer.deserialize(
                           show_subnet_res.body, content_type)['subnet']
        #TODO (Sumit): The assertion for the network_id needs to be different
        self.assertEqual({'id': subnet_id,
                          'cidr': new_cidr,
                          'network_id': subnet_data['network_id']},
                         subnet_data)
        LOG.debug("_test_update_subnet - format:%s - END", format)

    def _test_update_subnet_badrequest(self, format):
        LOG.debug("_test_update_subnet_badrequest - format:%s - START",
                  format)
        subnet_id = self._create_subnet(format)
        bad_body = {'subnet': {'bad-attribute': 'very-bad'}}
        update_subnet_req = testlib.\
                             update_subnet_request(self.tenant_id,
                                                    subnet_id, format,
                                                    custom_req_body=bad_body)
        update_subnet_res = update_subnet_req.get_response(self.api)
        self.assertEqual(update_subnet_res.status_int, 400)
        LOG.debug("_test_update_subnet_badrequest - format:%s - END",
                  format)

    def _test_update_subnet_not_found(self, format):
        LOG.debug("_test_update_subnet_not_found - format:%s - START",
                  format)
        new_cidr = '10.0.3.0/24'
        update_subnet_req = testlib.update_subnet_request(self.tenant_id,
                                                            "A BAD ID",
                                                            new_cidr,
                                                            format)
        update_subnet_res = update_subnet_req.get_response(self.api)
        self.assertEqual(update_subnet_res.status_int, 420)
        LOG.debug("_test_update_subnet_not_found - format:%s - END",
                  format)

    def _test_delete_subnet(self, format):
        LOG.debug("_test_delete_subnet - format:%s - START", format)
        content_type = "application/%s" % format
        subnet_id = self._create_subnet(format)
        LOG.debug("Deleting subnet %s"\
                  " of tenant %s" % (subnet_id, self.tenant_id))
        delete_subnet_req = testlib.subnet_delete_request(self.tenant_id,
                                                            subnet_id,
                                                            format)
        delete_subnet_res = delete_subnet_req.get_response(self.api)
        self.assertEqual(delete_subnet_res.status_int, 204)
        list_subnet_req = testlib.subnet_list_request(self.tenant_id,
                                                        format)
        list_subnet_res = list_subnet_req.get_response(self.api)
        subnet_list_data = self._subnet_serializer.deserialize(
                                list_subnet_res.body, content_type)
        subnet_count = len(subnet_list_data['subnets'])
        self.assertEqual(subnet_count, 0)
        LOG.debug("_test_delete_subnet - format:%s - END", format)

    def setUp(self):
        options = {}
        options['plugin_l3provider'] = test_config['l3plugin_name']
        self.api = server.APIRouterV1(options)
        self.tenant_id = "test_tenant"
        self.cidr = "10.0.0.0/24"
        self._subnet_serializer = \
            Serializer(server.subnets.Controller._serialization_metadata)

    def tearDown(self):
        """Clear the test environment"""
        # Remove database contents
        db.clear_db()

    def test_list_subnets_json(self):
        self._test_list_subnets('json')

    def test_list_subnets_xml(self):
        self._test_list_subnets('xml')

    def test_list_subnets_detail_json(self):
        self._test_list_subnets_detail('json')

    def test_list_subnets_detail_xml(self):
        self._test_list_subnets_detail('xml')

    def test_create_subnet_json(self):
        self._test_create_subnet('json')

    def test_create_subnet_xml(self):
        self._test_create_subnet('xml')

    def test_create_subnet_badrequest_json(self):
        self._test_create_subnet_badrequest('json')

    def test_create_subnet_badreqyest_xml(self):
        self._test_create_subnet_badrequest('xml')

    def test_show_subnet_not_found_json(self):
        self._test_show_subnet_not_found('json')

    def test_show_subnet_not_found_xml(self):
        self._test_show_subnet_not_found('xml')

    def test_show_subnet_json(self):
        self._test_show_subnet('json')

    def test_show_subnet_xml(self):
        self._test_show_subnet('xml')

    def test_show_subnet_detail_json(self):
        self._test_show_subnet_detail('json')

    def test_show_subnet_detail_xml(self):
        self._test_show_subnet_detail('xml')

    def test_delete_subnet_json(self):
        self._test_delete_subnet('json')

    def test_delete_subnet_xml(self):
        self._test_delete_subnet('xml')

    def test_update_subnet_json(self):
        self._test_update_subnet('json')

    def test_update_subnet_xml(self):
        self._test_update_subnet('xml')

    def test_update_subnet_badrequest_json(self):
        self._test_update_subnet_badrequest('json')

    def test_unparsable_data_xml(self):
        self._test_unparsable_data('xml')

    def test_unparsable_data_json(self):
        self._test_unparsable_data('json')
