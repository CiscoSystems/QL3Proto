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
#    @author: Shubhangi Satras, Cisco Systems
""" Class for testing CLI for routetables"""
import logging as LOG
#from quantum.common.serializer import Serializer
#from quantum.client.l3client.l3client import Client
#from quantum.tests.unit.l3.test_l3clientlib import *
from quantum.tests.unit.l3.test_l3clientlib import L3CLIAPITest

#LOG = logging.getLogger(__name__)


class L3SRoutetableCLIAPITest(L3CLIAPITest):
    """ Class for testing CLI for routetables """

    def _test_list_routetables(self, tenant='TENANT_1',
                               format='json', status=200):
        """Tests proper listing of routetable """
        LOG.debug("_test_list_routetable - tenant:%s "\
                  "- format:%s - START", format, tenant)
        self._assert_sanity(self.client.list_routetables,
                            status,
                            "GET",
                            "routetables",
                            data=[],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_list_routetables - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_show_routetable_details(self, tenant='TENANT_1',
                                      format='json', status=200):
        """Tests show routetable in detail """
        LOG.debug("_test_show_routetable_details - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.show_routetable_details,
                            status,
                            "GET",
                            "routetables/001",
                            data=["001"],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_show_routetable_details - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_create_routetable(self, tenant='TENANT_1',
                                format='json', status=200):
        """Tests creation of routetable"""
        LOG.debug("_test_create_routetable - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.create_routetable,
                            status,
                            "POST",
                            "routetables",
                            data=[{'routetable': {}}],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_create_routetable - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_update_routetable(self, tenant='TENANT_1',
                                format='json', status=200):
        """ Tests updation of routetable"""
        LOG.debug("_test_update_routetable - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.update_routetable,
                            status,
                            "PUT",
                            "routetables/001",
                            data=["001",
                                  {'routetable': {}}],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_update_routetable - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_delete_routetable(self, tenant='TENANT_1',
                                format='json', status=200):
        """ Tests the deletion of the routetable"""
        LOG.debug("_test_delete_routetable - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.delete_routetable,
                            status,
                            "DELETE",
                            "routetables/001",
                            data=["001"],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_delete_routetable - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def test_list_rt_json(self):
        """Tests listing of routetable for json as request """
        self._test_list_routetables(format='json')

    def test_list_rt_xml(self):
        """Tests listing of routetable for xml as request """
        self._test_list_routetables(format='xml')

    def test_list_rt_alt_tenant(self):
        """Tests listing of routetable for alternate tenant """
        self._test_list_routetables(tenant='TENANT_2')

    def test_list_rt_error_470(self):
        """Tests listof routetable for Service Unavailable(API not supported"""
        self._test_list_routetables(status=470)

    def test_list_rt_error_401(self):
        """Tests listing of routetable for Unauthorized """
        self._test_list_routetables(status=401)

    def test_show_rt_details_json(self):
        """Tests show routetable for json format """
        self._test_show_routetable_details(format='json')

    def test_show_rt_details_xml(self):
        """Tests show routetable for xml format"""
        self._test_show_routetable_details(format='xml')

    def test_show_rt_details_alt_tenant(self):
        """Tests show routetable for detail for alternate tenant"""
        self._test_show_routetable_details(tenant='TENANT_2')

    def test_show_rt_details_error_470(self):
        """Tests show routetable for Service Unavailable(API not supported)"""
        self._test_show_routetable_details(status=470)

    def test_show_rt_details_error_401(self):
        """Tests show routetable for Unauthorized """
        self._test_show_routetable_details(status=401)

    def test_show_rt_details_error_460(self):
        """Tests show routetable in detail for routetable not found """
        self._test_show_routetable_details(status=460)

    def test_create_rt_json(self):
        """Tests creation of routetable for json as request """
        self._test_create_routetable(format='json')

    def test_create_rt_xml(self):
        """Tests creation of routetable for xml as request """
        self._test_create_routetable(format='xml')

    def test_create_rt_alt_tenant(self):
        """Tests Create routetable for detail for alternate tenant"""
        self._test_create_routetable(tenant='TENANT_2')

    def test_create_rt_error_470(self):
        """Test Create routetable for Service Unavailable(API not supported)"""
        self._test_create_routetable(status=470)

    def test_create_rt_error_401(self):
        """Tests Create routetable for Unauthorized """
        self._test_create_routetable(status=401)

    def test_create_rt_error_400(self):
        """Tests Create routetable for Malformed URL """
        self._test_create_routetable(status=400)

    def test_update_rt_json(self):
        """Tests Update routetable for json format """
        self._test_update_routetable(format='json')

    def test_update_rt_xml(self):
        """Tests Update routetable for xml format """
        self._test_update_routetable(format='xml')

    def test_update_rt_alt_tenant(self):
        """Tests Update routetable for detail for alternate tenant"""
        self._test_update_routetable(tenant='TENANT_2')

    def test_update_rt_error_470(self):
        """Test Update routetable for Service Unavailable(API not supported)"""
        self._test_update_routetable(status=470)

    def test_update_rt_error_401(self):
        """Tests Update routetable for Unauthorized """
        self._test_update_routetable(status=401)

    def test_update_rt_error_400(self):
        """Tests Update routetable for Malformed URL """
        self._test_update_routetable(status=400)

    def test_update_rt_error_460(self):
        """Test update Routetable for Routable not found"""
        self._test_update_routetable(status=460)

    def test_delete_rt_json(self):
        """Tests deletion of routetable in with request sent in json format"""
        self._test_delete_routetable(format='json')

    def test_delete_rt_xml(self):
        """Tests deletion of routetable in with request sent in xml format"""
        self._test_delete_routetable(format='xml')

    def test_delete_rt_alt_tenant(self):
        """Tests Update routetable for detail for alternate tenant"""
        self._test_delete_routetable(tenant='TENANT_2')

    def test_delete_rt_error_470(self):
        """Test Update routetable for Service Unavailable(API not supported)"""
        self._test_delete_routetable(status=470)

    def test_delete_rt_error_401(self):
        """Tests Update routetable for Unauthorized """
        self._test_delete_routetable(status=401)

    def test_delete_rt_error_460(self):
        """Test update Routetable for Routable not found"""
        self._test_delete_routetable(status=460)
