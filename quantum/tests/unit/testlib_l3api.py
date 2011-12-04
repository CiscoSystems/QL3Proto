import webob

from quantum.common.serializer import Serializer


def create_request(path, body, content_type, method='GET'):
    req = webob.Request.blank(path)
    req.method = method
    req.headers = {}
    req.headers['Accept'] = content_type
    req.body = body
    return req


def _subnet_list_request(tenant_id, format='xml', detail=False):
    method = 'GET'
    detail_str = detail and '/detail' or ''
    path = "/tenants/%(tenant_id)s/subnets" \
           "%(detail_str)s.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)


def subnet_list_request(tenant_id, format='xml'):
    return _subnet_list_request(tenant_id, format)


def subnet_list_detail_request(tenant_id, format='xml'):
    return _subnet_list_request(tenant_id, format, detail=True)


def _show_subnet_request(tenant_id, subnet_id, format='xml', detail=False):
    method = 'GET'
    detail_str = detail and '/detail' or ''
    path = "/tenants/%(tenant_id)s/subnets" \
           "/%(subnet_id)s%(detail_str)s.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)


def show_subnet_request(tenant_id, subnet_id, format='xml'):
    return _show_subnet_request(tenant_id, subnet_id, format)


def show_subnet_detail_request(tenant_id, subnet_id, format='xml'):
    return _show_subnet_request(tenant_id, subnet_id, format, detail=True)


def new_subnet_request(tenant_id, cidr='10.0.0.0/16',
                        format='xml', custom_req_body=None):
    method = 'POST'
    path = "/tenants/%(tenant_id)s/subnets.%(format)s" % locals()
    data = custom_req_body or {'subnet': {'cidr': '%s' % cidr}}
    content_type = "application/%s" % format
    body = Serializer().serialize(data, content_type)
    return create_request(path, body, content_type, method)


def update_subnet_request(tenant_id, subnet_id, cidr, format='xml',
                           custom_req_body=None):
    method = 'PUT'
    path = "/tenants/%(tenant_id)s/subnets" \
           "/%(subnet_id)s.%(format)s" % locals()
    data = custom_req_body or {'subnet': {'cidr': '%s' % cidr}}
    content_type = "application/%s" % format
    body = Serializer().serialize(data, content_type)
    return create_request(path, body, content_type, method)


def subnet_delete_request(tenant_id, subnet_id, format='xml'):
    method = 'DELETE'
    path = "/tenants/%(tenant_id)s/subnets/" \
           "%(subnet_id)s.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)
