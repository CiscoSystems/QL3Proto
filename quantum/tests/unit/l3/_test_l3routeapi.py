import logging
import re

import quantum.tests.unit.l3.testlib_l3routeapi as testlib

from quantum.tests.unit.l3._test_l3api import *
#from quantum.wsgi import XMLDeserializer, JSONDeserializer

LOG = logging.getLogger(__name__)

ROUTES = 'routes'
regex = "([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})"


class L3RouteAbstractAPITest(L3AbstractAPITest):

    """
    Route API test class
    """

    def _create_route(self, format, routetable_id,
                      custom_req_body=None, expected_res_status=202):
        """
        Create route helper function.
        """
        LOG.debug("Creating route")
        content_type = "application/" + format
        route_req = testlib.new_route_request(self.tenant_id,
                                              routetable_id,
                                              format,
                                              custom_req_body)
        route_res = route_req.get_response(self.api)
        self.assertEqual(route_res.status_int, expected_res_status)
        if expected_res_status in (RESPONSE_CODE_CREATE, RESPONSE_CODE_OTHERS):
            route_data = self._route_deserializers[content_type].\
                    deserialize(route_res.body)['body']
            return route_data

    def _test_create_route(self, format):
        """
        Test API create_route
        """
        LOG.debug("_test_create_route - format:%s - START", format)
        content_type = "application/%s" % format
        routetable_id = self._create_routetable_id(format)
        route_id = self._create_route_id(format, routetable_id)
        show_route_req = testlib.show_route_request(self.tenant_id,
                                                    routetable_id,
                                                    route_id,
                                                    format)
        show_route_res = show_route_req.get_response(self.api)
        show_route_res_data = self._route_deserializers[\
               content_type].deserialize(show_route_res.body)['body']
        show_route_res_id = (re.findall(regex, str(show_route_res_data)))[1]
        self.assertEqual(show_route_res_id, route_id)
        LOG.debug("_test_create_route - format:%s - END", format)

    def _test_create_route_badrequest(self, format):
        """
        Test API create_route with a bad request
        """
        LOG.debug("_test_create_route_badrequest - format:%s - START",
                  format)
        bad_body = {'bad-attribule': {'bad': 'bad'}}
        routetable_id = self._create_routetable_id(format)
        self._create_route(format, routetable_id,
                                 custom_req_body=bad_body,
                                 expected_res_status=400)
        LOG.debug("_test_create_route_badrequest - format:%s - END",
                  format)

    def _test_show_route(self, format):
        """
        Test API show_route
        """
        LOG.debug("_test_show_route - format:%s - START", format)
        content_type = "application/%s" % format
        routetable_id = self._create_routetable_id(format)
        route_id = self._create_route_id(format, routetable_id)
        show_route_req = testlib.show_route_request(self.tenant_id,
                                                    routetable_id,
                                                    route_id,
                                                    format)
        show_route_res = show_route_req.get_response(self.api)
        show_route_res_data = self._route_deserializers[\
                content_type].deserialize(show_route_res.body)['body']
        show_route_res_id = (re.findall(regex, str(show_route_res_data)))[1]
        self.assertEqual(show_route_res_id, route_id)
        LOG.debug("_test_show_route - format:%s - END", format)

    def _test_show_route_detail(self, format):
        """
        Test API show_route with detail
        """
        LOG.debug("_test_show_route_detail - format:%s - START", format)
        content_type = "application/%s" % format
        routetable_id = self._create_routetable_id(format)
        route_id = self._create_route_id(format, routetable_id)
        show_route_req = testlib.show_route_detail_request(self.tenant_id,
                                                           routetable_id,
                                                           route_id,
                                                           format)
        show_route_res = show_route_req.get_response(self.api)
        show_route_res_data = self._route_deserializers[\
                content_type].deserialize(show_route_res.body)['body']
        show_route_res_id = (re.findall(regex, str(show_route_res_data)))[1]
        self.assertEqual(show_route_res_id, route_id)
        LOG.debug("_test_show_route_detail - format:%s - END", format)

    def _test_show_route_not_found(self, format):
        """
        Test API show_route with route not found
        """
        LOG.debug("_test_show_route_not_found - format:%s - START",
                  format)
        LOG.debug("Creating subnet")
        show_route_req = testlib.show_route_request(self.tenant_id,
                                                    "BAD",
                                                    "BAD",
                                                    format)
        show_route_res = show_route_req.get_response(self.api)
        self.assertEqual(show_route_res.status_int, 465)
        LOG.debug("_test_show_route_not_found - format:%s - END", format)

    def _test_list_routes(self, format):
        """
        Test API list_route
        """
        LOG.debug("_test_list_routes - format:%s - START", format)
        routetable_id = self._create_routetable_id(format)
        list_route_req = testlib.route_list_request(self.tenant_id,
                                                    routetable_id,
                                                    format)
        list_route_res = list_route_req.get_response(self.api)
        self.assertEqual(list_route_res.status_int, 200)
        LOG.debug("_test_list_routes - format:%s - END", format)

    def _test_list_routes_detail(self, format):
        """
        Test API list_route with detail
        """
        LOG.debug("_test_list_routes - format:%s - START", format)
        routetable_id = self._create_routetable_id(format)
        list_route_req = testlib.route_list_detail_request(self.tenant_id,
                                                    routetable_id,
                                                    format)
        list_route_res = list_route_req.get_response(self.api)
        self.assertEqual(list_route_res.status_int, 200)
        LOG.debug("_test_list_routes - format:%s - END", format)

    def _test_delete_route(self, format):
        """
        Test API delete_route
        """
        LOG.debug("_test_delete_route - format:%s - START", format)
        routetable_id = self._create_routetable_id(format)
        route_id = self._create_route_id(format, routetable_id)
        delete_route_req = testlib.route_delete_request(self.tenant_id,
                                                    routetable_id, route_id,
                                                    format)
        delete_route_res = delete_route_req.get_response(self.api)
        self.assertEqual(delete_route_res.status_int, 204)
        LOG.debug("_test_delete_route - format:%s - END", format)

    def _create_route_id(self, format, routetable_id):
        """
        return route ID for request bodies
        """
        LOG.debug("_create_route_id - START")
        content_type = "application/%s" % format
        route_req = testlib.new_route_request(self.tenant_id, routetable_id,
                                                          format)
        route_res = route_req.get_response(self.api)
        route_res_data = self._route_deserializers[\
                content_type].deserialize(route_res.body)['body']
        route_id = (re.findall(regex, str(route_res_data)))[1]
        LOG.debug("_create_route_id - END")
        return route_id

    def _create_routetable_id(self, format):
        """
        return routetable ID for request bodies
        """
        LOG.debug("_create_routetable_id - START")
        routetable_req = testlib.new_routetable_request(self.tenant_id,
                                                        format,
                                                        None)
        routetable_res = routetable_req.get_response(self.api)
        routetable_id = (re.findall(regex, str(routetable_res)))[0]
        LOG.debug("_create_routetable_id - END")
        return routetable_id

    def setUp(self, api_router_klass, xml_metadata_dict):
        super(L3RouteAbstractAPITest, self).setUp(api_router_klass,
                                                   xml_metadata_dict)
        self.tenant_id = "test_tenant"
        self.cidr = "10.0.0.0/24"
        route_xml_deserializer = XMLDeserializer(
                xml_metadata_dict[ROUTES])
        json_deserializer = JSONDeserializer()
        self._route_deserializers = {
            'application/xml': route_xml_deserializer,
            'application/json': json_deserializer,
        }

    def tearDown(self):
        super(L3RouteAbstractAPITest, self).tearDown()

    def test_create_route_json(self):
        """
        create_route with json format
        """
        self._test_create_route('json')

    def test_create_route_xml(self):
        """
        create_route with xml format
        """
        self._test_create_route('xml')

    def test_create_route_badreq_json(self):
        """
        create_route with json format and bad req
        """
        self._test_create_route_badrequest('json')

    def test_create_route_badreq_xml(self):
        """
        create_route with xml format and bad req
        """
        self._test_create_route_badrequest('xml')

    def test_list_routes_json(self):
        """
        list_route with json format
        """
        self._test_list_routes('json')

    def test_list_routes_xml(self):
        """
        list_route with xml format
        """
        self._test_list_routes('xml')

    def test_list_routes_detail_json(self):
        """
        list_route with json format and detail
        """
        self._test_list_routes_detail('json')

    def test_list_routes_detail_xml(self):
        """
        list_route with xml format and detail
        """
        self._test_list_routes_detail('xml')

    def test_show_route_not_found_json(self):
        """
        show_route with json format, no route found
        """
        self._test_show_route_not_found('json')

    def test_show_route_not_found_xml(self):
        """
        show_route with xml format, no route found
        """
        self._test_show_route_not_found('xml')

    def test_show_route_json(self):
        """
        show_route with json format
        """
        self._test_show_route('json')

    def test_show_route_xml(self):
        """
        show_route with xml format
        """
        self._test_show_route('xml')

    def test_show_route_detail_json(self):
        """
        show_route with json format and detail
        """
        self._test_show_route_detail('json')

    def test_show_route_detail_xml(self):
        """
        show_route with xml format and detail
        """
        self._test_show_route_detail('xml')

    def test_delete_route_json(self):
        """
        delete_route with json format
        """
        self._test_delete_route('json')

    def test_delete_route_xml(self):
        """
        delete_route with xml format
        """
        self._test_delete_route('xml')
