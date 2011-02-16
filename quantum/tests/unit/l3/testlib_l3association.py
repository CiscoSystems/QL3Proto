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
"""Testlib for L3Association API tests"""
# pylint: disable-msg=W0613

import webob

from quantum.common.serializer import Serializer


def create_request(path, body, content_type, method='GET'):
    """creating request"""
    req = webob.Request.blank(path)
    req.method = method
    req.headers = {}
    req.headers['Accept'] = content_type
    req.body = body
    return req


def new_association_request(tenant_id, subnet_id, routetable_id,
                            format='xml', custom_req_body=None):
    """creting request for new association"""
    method = 'PUT'
    path = "/tenants/%(tenant_id)s/subnets" \
           "/%(subnet_id)s/association.%(format)s" % locals()
    data = custom_req_body or {
            'association': {'routetable_id': '%s' % routetable_id}}
    content_type = "application/%s" % format
    body = Serializer().serialize(data, content_type)
    return create_request(path, body, content_type, method)


def _show_association_request(tenant_id, subnet_id,
                              format='xml', detail=False):
    """creting request for show association"""
    method = 'GET'
    detail_str = detail and '/detail' or ''
    path = "/tenants/%(tenant_id)s/subnets" \
           "/%(subnet_id)s/association%(detail_str)s.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)


def show_association_request(tenant_id, subnet_id, format='xml'):
    """creting request for show association"""
    return _show_association_request(tenant_id, subnet_id, format)


def association_delete_request(tenant_id, subnet_id,
                               routetable_id, format='xml'):
    """creting request for deleting association"""
    method = 'DELETE'
    path = "/tenants/%(tenant_id)s/subnets" \
           "/%(subnet_id)s/association.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)


def new_subnet_request(tenant_id, cidr='10.0.0.0/16',
                        format='xml', custom_req_body=None):
    """creting request for a new subnet"""
    method = 'POST'
    path = "/tenants/%(tenant_id)s/subnets.%(format)s" % locals()
    data = custom_req_body or {'subnet': {'cidr': '%s' % cidr}}
    content_type = "application/%s" % format
    body = Serializer().serialize(data, content_type)
    return create_request(path, body, content_type, method)


def new_routetable_request(tenant_id, format='xml', custom_req_body=None):
    """creting request for a new routetable"""
    label = 'label'
    method = 'POST'
    path = "/tenants/%(tenant_id)s/routetables.%(format)s" % locals()
    data = custom_req_body or {'routetable': {'label': '%s' % label}}
    content_type = "application/%s" % format
    body = Serializer().serialize(data, content_type)
    return create_request(path, body, content_type, method)
