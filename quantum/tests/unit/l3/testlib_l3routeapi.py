import webob

from quantum.common.serializer import Serializer


def create_request(path, body, content_type, method='GET'):
    """
    Return complete request
    """
    req = webob.Request.blank(path)
    req.method = method
    req.headers = {}
    req.headers['Accept'] = content_type
    req.body = body
    return req


def new_route_request(tenant_id, routetable_id, format='xml',
                      custom_req_body=None):
    """
    Return request for create_route
    """
    method = 'POST'
    path = "/tenants/%(tenant_id)s/routetables/%(routetable_id)s/routes" \
           ".%(format)s" % locals()
    content_type = "application/%s" % format
    data = custom_req_body or {'route': {'source': '10.0.0.1',
                               'destination': '1.1.1.1',
                               'target': 'pc'}}
    body = Serializer().serialize(data, content_type)
    return create_request(path, body, content_type, method)


def new_routetable_request(tenant_id, format='xml', custom_req_body=None):
    label = 'label'
    method = 'POST'
    path = "/tenants/%(tenant_id)s/routetables.%(format)s" % locals()
    data = custom_req_body or {'routetable': {'label': '%s' % label}}
    content_type = "application/%s" % format
    body = Serializer().serialize(data, content_type)
    return create_request(path, body, content_type, method)


def _route_list_request(tenant_id, routetable_id, format='xml', detail=False):
    """
    Return request for list_routes
    """
    method = 'GET'
    detail_str = detail and '/detail' or ''
    path = "/tenants/%(tenant_id)s/routetables/%(routetable_id)s/routes" \
           "%(detail_str)s.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)


def _show_route_request(tenant_id, routetable_id, route_id,
                        format='xml', detail=False):
    """
    Return request for show_route
    """
    method = 'GET'
    detail_str = detail and '/detail' or ''
    path = "/tenants/%(tenant_id)s/routetables/%(routetable_id)s/" \
           "routes/%(route_id)s%(detail_str)s.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)


def show_route_request(tenant_id, routetable_id, route_id, format='xml'):
    """
    Make request for show_route
    """
    return _show_route_request(tenant_id, routetable_id, route_id, format)


def show_route_detail_request(tenant_id, routetable_id, route_id,
                              format='xml'):
    """
    Make request for show_route with detail
    """
    return _show_route_request(tenant_id, routetable_id, route_id,
                               format, detail=True)


def route_delete_request(tenant_id, routetable_id, route_id, format='xml',
                         detail=False):
    """
    Make request for route_delete
    """
    method = 'DELETE'
    path = "/tenants/%(tenant_id)s/routetables/%(routetable_id)s/routes/" \
           "%(route_id)s.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)


def route_list_request(tenant_id, routetable_id, format='xml'):
    """
    Make request for route_list
    """
    return _route_list_request(tenant_id, routetable_id, format)


def route_list_detail_request(tenant_id, routetable_id, format='xml'):
    """
    Make request for route_list with detail
    """
    return _route_list_request(tenant_id, routetable_id, format, detail=True)
