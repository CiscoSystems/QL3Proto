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
#    @author: Sumit Naiksatam, Cisco Systems

import logging
import unittest
import re

from quantum.common.serializer import Serializer
from quantum.client.l3client.l3client import Client
from quantum.tests.unit.l3.test_l3clientlib import *

LOG = logging.getLogger(__name__)


class L3SubnetCLIAPITest(L3CLIAPITest):
    """
    Unit test class for subnet CLI
    """

    def _test_list_subnets(self, tenant=TENANT_1, format='json', status=200):
        """
        list_subnets CLI test
        """
        LOG.debug("_test_list_subnet - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.list_subnets,
                            status,
                            "GET",
                            "subnets",
                            data=[],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_list_subnets - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_show_subnet_details(self,
                                   tenant=TENANT_1, format='json', status=200):
        """
        show_subnet CLI test
        """
        LOG.debug("_test_show_subnet_details - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.show_subnet_details,
                            status,
                            "GET",
                            "subnets/001",
                            data=["001"],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_show_subnet_details - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_create_subnet(self, tenant=TENANT_1, format='json', status=200):
        """
        create_subnet CLI test
        """
        LOG.debug("_test_create_subnet - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.create_subnet,
                            status,
                            "POST",
                            "subnets",
                            data=[{'subnet': {'cidr': '10.0.0.0/24'}}],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_create_subnet - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_update_subnet(self, tenant=TENANT_1, format='json', status=200):
        """
        update_subnet CLI test
        """
        LOG.debug("_test_update_subnet - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.update_subnet,
                            status,
                            "PUT",
                            "subnets/001",
                            data=["001",
                                  {'subnet': {'cidr': '10.0.1.0/24'}}],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_update_subnet - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_delete_subnet(self, tenant=TENANT_1, format='json', status=200):
        """
        delete_subnet CLI test
        """
        LOG.debug("_test_delete_subnet - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.delete_subnet,
                            status,
                            "DELETE",
                            "subnets/001",
                            data=["001"],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_delete_subnet - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def test_list_subnets_json(self):
        """
        list_subnets CLI test, json format
        """
        self._test_list_subnets(format='json')

    def test_list_subnets_xml(self):
        """
        list_subnets CLI test, xml format
        """
        self._test_list_subnets(format='xml')

    def test_list_subnets_alt_tenant(self):
        """
        list_subnets CLI test, with alternate tenant
        """
        self._test_list_subnets(tenant=TENANT_2)

    def test_list_subnets_error_470(self):
        """
        list_subnets CLI test, expected error 470
        """
        self._test_list_subnets(status=470)

    def test_list_subnets_error_401(self):
        """
        list_subnets CLI test, expected error 401
        """
        self._test_list_subnets(status=401)

    def test_show_subnet_details_json(self):
        """
        show_subnet CLI test, json format with detail
        """
        self._test_show_subnet_details(format='json')

    def test_show_subnet_details_xml(self):
        """
        show_subnet CLI test, xml format with detail
        """
        self._test_show_subnet_details(format='xml')

    def test_show_sb_details_alt_tenant(self):
        """
        show_subnet CLI test, detail with alternate tenant
        """
        self._test_show_subnet_details(tenant=TENANT_2)

    def test_show_sb_details_error_470(self):
        """
        show_subnet CLI test, expected error 470
        """
        self._test_show_subnet_details(status=470)

    def test_show_sb_details_error_401(self):
        """
        show_subnet CLI test, expected error 401
        """
        self._test_show_subnet_details(status=401)

    def test_show_sb_details_error_450(self):
        """
        show_subnet CLI test, expected error 450
        """
        self._test_show_subnet_details(status=450)

    def test_create_subnet_json(self):
        """
        create_subnet CLI test, json format
        """
        self._test_create_subnet(format='json')

    def test_create_subnet_xml(self):
        """
        create_subnet CLI test, xml format
        """
        self._test_create_subnet(format='xml')

    def test_create_subnet_alt_tenant(self):
        """
        create_subnet CLI test, with alternate tenant
        """
        self._test_create_subnet(tenant=TENANT_2)

    def test_create_subnet_error_470(self):
        """
        create_subnet CLI test, expected error 470
        """
        self._test_create_subnet(status=470)

    def test_create_subnet_error_401(self):
        """
        create_subnet CLI test, expected error 401
        """
        self._test_create_subnet(status=401)

    def test_create_subnet_error_400(self):
        """
        create_subnet CLI test, expected error 400
        """
        self._test_create_subnet(status=400)

    def test_update_subnet_json(self):
        """
        update_subnet CLI test, json format
        """
        self._test_update_subnet(format='json')

    def test_update_subnet_xml(self):
        """
        update_subnet CLI test, xml format
        """
        self._test_update_subnet(format='xml')

    def test_update_subnet_alt_tenant(self):
        """
        update_subnet CLI test, with alternate tenant
        """
        self._test_update_subnet(tenant=TENANT_2)

    def test_update_subnet_error_470(self):
        """
        update_subnet CLI test, expected error 470
        """
        self._test_update_subnet(status=470)

    def test_update_subnet_error_401(self):
        """
        update_subnet CLI test, expected error 401
        """
        self._test_update_subnet(status=401)

    def test_update_subnet_error_400(self):
        """
        update_subnet CLI test, expected error 400
        """
        self._test_update_subnet(status=400)

    def test_update_subnet_error_450(self):
        """
        update_subnet CLI test, expected error 450
        """
        self._test_update_subnet(status=450)

    def test_delete_subnet_json(self):
        """
        delete_subnet CLI test, json format
        """
        self._test_delete_subnet(format='json')

    def test_delete_subnet_xml(self):
        """
        delete_subnet CLI test, xml format
        """
        self._test_delete_subnet(format='xml')

    def test_delete_subnet_alt_tenant(self):
        """
        delete_subnet CLI test, with alternate tenant
        """
        self._test_delete_subnet(tenant=TENANT_2)

    def test_delete_subnet_error_470(self):
        """
        delete_subnet CLI test, expected error 470
        """
        self._test_delete_subnet(status=470)

    def test_delete_subnet_error_401(self):
        """
        delete_subnet CLI test, expected error 401
        """
        self._test_delete_subnet(status=401)

    def test_delete_subnet_error_450(self):
        """
        delete_subnet CLI test, expected error 450
        """
        self._test_delete_subnet(status=450)

    def test_delete_subnet_error_451(self):
        """
        delete_subnet CLI test, expected error 451
        """
        self._test_delete_subnet(status=451)
