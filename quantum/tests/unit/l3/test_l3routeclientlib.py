"""Class for testing CLI calls """
import logging as LOG
#import unittest
#import re

#from quantum.common.serializer import Serializer
#from quantum.client.l3client.l3client import Client
#from quantum.tests.unit.l3.test_l3clientlib import *
from quantum.tests.unit.l3.test_l3clientlib import L3CLIAPITest
#LOG = logging.getLogger(__name__)


class L3RouteCLIAPITest(L3CLIAPITest):

    """
    CLI tests for l3 routes
    """

    def _test_list_routes(self, tenant='TENANT_1', routetable_id="???",
                           format='json', status=200):
        """
        CLI test list_routes
        """
        LOG.debug("_test_list_routes - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.list_routes,
                            status,
                            "GET",
                            "routetables/001/routes",
                            data=["001"],
                            params={'tenant': tenant,
                                    'routetable_id': routetable_id,
                                    'format': format})

        LOG.debug("_test_list_routes - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_show_route_details(self, tenant='TENANT_1', 
                                 format='json', status=200):
        """
        CLI test show_route with detail
        """
        LOG.debug("_test_show_route_details - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.show_route_details,
                            status,
                            "GET",
                            "routetables/001/routes/002",
                            data=["001", "002"],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_show_route_details - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_create_route(self, tenant='TENANT_1', format='json', status=200):
        """
        CLI test create_route
        """
        LOG.debug("_test_create_route - tenant:%s "\
                  "- format:%s - START", format, tenant)
        self._assert_sanity(self.client.create_route,
                            status,
                            "POST",
                            "routetables/007/routes",
                            data=["007"],
                            params={'tenant': tenant, 'format': format})
        LOG.debug("_test_create_route - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_delete_route(self, tenant='TENANT_1', format='json', status=200):
        """
        CLI test delete_route
        """
        LOG.debug("_test_delete_route - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.delete_route,
                            status,
                            "DELETE",
                            "routetables/001/routes/002",
                            data=["001", "002"],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_delete_route - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def test_list_routes_xml(self):
        """
        CLI test list_routes xml
        """
        self._test_list_routes(format='xml')

    def test_list_routes_json(self):
        """
        CLI test list_routes json
        """
        self._test_list_routes(format='json')

    def test_show_route_details_xml(self):
        """
        CLI test show_route with detail
        """
        self._test_show_route_details(format='xml')

    def test_show_route_details_error_470(self):
        """
        CLI test show_route with detail expected error 470
        """
        self._test_show_route_details(status=470)

    def test_show_route_details_error_401(self):
        """
        CLI test show_route with detail expected error 401
        """
        self._test_show_route_details(status=401)

    def test_show_route_details_error_450(self):
        """
        CLI test show_route with detail expected error 450
        """
        self._test_show_route_details(status=450)

    def test_create_route_json(self):
        """
        CLI test create_route json
        """
        self._test_create_route(format='json')

    def test_create_route_xml(self):
        """
        CLI test create_route xml
        """
        self._test_create_route(format='xml')

    def test_create_route_error_470(self):
        """
        CLI test create_route expected error 470
        """
        self._test_create_route(status=470)

    def test_create_route_error_401(self):
        """
        CLI test create_route expected error 401
        """
        self._test_create_route(status=401)

    def test_create_route_error_400(self):
        """
        CLI test create_route expected error 400
        """
        self._test_create_route(status=400)

    def test_delete_route_json(self):
        """
        CLI test delete_route json
        """
        self._test_delete_route(format='json')

    def test_delete_route_xml(self):
        """
        CLI test delete_route xml
        """
        self._test_delete_route(format='xml')

    def test_delete_route_error_470(self):
        """
        CLI test delete_route expected error 470
        """
        self._test_delete_route(status=470)

    def test_delete_route_error_401(self):
        """
        CLI test delete_route expected error 401
        """
        self._test_delete_route(status=401)

    def test_delete_route_error_450(self):
        """
        CLI test delete_route expected error 450
        """
        self._test_delete_route(status=450)

    def test_delete_route_error_451(self):
        """
        CLI test delete_route expected error 451
        """
        self._test_delete_route(status=451)
