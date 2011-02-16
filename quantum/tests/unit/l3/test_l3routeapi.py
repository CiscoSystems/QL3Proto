import quantum.api.l3routes as l3routes
import quantum.tests.unit.l3._test_l3routeapi as test_api

from quantum.common.test_lib import test_config


class L3RouteAPITestV11(test_api.L3RouteAbstractAPITest):

    def assert_route(self, **kwargs):
        self.assertEqual({'routetable_id': kwargs['routetable_id']},
                         kwargs['route_data'])

    def assert_route_details(self, **kwargs):
        self.assertEqual({'routetable_id': kwargs['routetable_id']},
                         kwargs['route_data'])

    def setUp(self):
        super(L3RouteAPITestV11, self).setUp('quantum.api.APIRouterV11',
             {test_api.ROUTES: l3routes.ControllerV11._serialization_metadata})
