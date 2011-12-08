# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011 Nicira Networks, Inc.
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
# @author: Somik Behera, Nicira Networks, Inc.
# @author: Brad Hall, Nicira Networks, Inc.
# @author: Dan Wendlandt, Nicira Networks, Inc.
# @author: Sumit Naiksatam, Cisco Systems, Inc.

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc

from quantum.common import exceptions as q_exc
from quantum.db import models


_ENGINE = None
_MAKER = None
BASE = models.BASE
LOG = logging.getLogger('quantum.db.api')


def configure_db(options):
    """
    Establish the database, create an engine if needed, and
    register the models.

    :param options: Mapping of configuration options
    """
    global _ENGINE
    if not _ENGINE:
        _ENGINE = create_engine(options['sql_connection'],
                                echo=False,
                                echo_pool=True,
                                pool_recycle=3600)
        register_models()


def clear_db():
    global _ENGINE
    assert _ENGINE
    for table in reversed(BASE.metadata.sorted_tables):
        _ENGINE.execute(table.delete())


def get_session(autocommit=True, expire_on_commit=False):
    """Helper method to grab session"""
    global _MAKER, _ENGINE
    if not _MAKER:
        assert _ENGINE
        _MAKER = sessionmaker(bind=_ENGINE,
                              autocommit=autocommit,
                              expire_on_commit=expire_on_commit)
    return _MAKER()


def register_models():
    """Register Models and create properties"""
    global _ENGINE
    assert _ENGINE
    BASE.metadata.create_all(_ENGINE)


def unregister_models():
    """Unregister Models, useful clearing out data before testing"""
    global _ENGINE
    assert _ENGINE
    BASE.metadata.drop_all(_ENGINE)


def _check_duplicate_net_name(tenant_id, net_name):
    """Checks whether a network with the same name
       already exists for the tenant.
    """

    #TODO(salvatore-orlando): Not used anymore - candidate for removal
    session = get_session()
    try:
        net = session.query(models.Network).\
          filter_by(tenant_id=tenant_id, name=net_name).\
          one()
        raise q_exc.NetworkNameExists(tenant_id=tenant_id,
                        net_name=net_name, net_id=net.uuid)
    except exc.NoResultFound:
        # this is the "normal" path, as API spec specifies
        # that net-names are unique within a tenant
        pass


def _check_duplicate_cidr(tenant_id, cidr):
    """Checks whether a subnet with the same cidr
       already exists for the tenant.
    """

    #TODO(salvatore-orlando): Not used anymore - candidate for removal
    session = get_session()
    try:
        subnet = session.query(models.Subnet).\
          filter_by(tenant_id=tenant_id, cidr=cidr).\
          one()
        raise q_exc.NetworkNameExists(tenant_id=tenant_id,
                        cidr=cidr, subnet_id=subnet.uuid)
    except exc.NoResultFound:
        # this is the "normal" path, as API spec specifies
        # that net-names are unique within a tenant
        pass


def network_create(tenant_id, name):
    session = get_session()

    with session.begin():
        net = models.Network(tenant_id, name)
        session.add(net)
        session.flush()
        return net


def network_list(tenant_id):
    session = get_session()
    return session.query(models.Network).\
      filter_by(tenant_id=tenant_id).\
      all()


def network_get(net_id):
    session = get_session()
    try:
        return  session.query(models.Network).\
            filter_by(uuid=net_id).\
            one()
    except exc.NoResultFound, e:
        raise q_exc.NetworkNotFound(net_id=net_id)


def network_update(net_id, tenant_id, **kwargs):
    session = get_session()
    net = network_get(net_id)
    for key in kwargs.keys():
        if key == "name":
            _check_duplicate_net_name(tenant_id, kwargs[key])
        net[key] = kwargs[key]
    session.merge(net)
    session.flush()
    return net


def network_destroy(net_id):
    session = get_session()
    try:
        net = session.query(models.Network).\
          filter_by(uuid=net_id).\
          one()

        ports = session.query(models.Port).\
            filter_by(network_id=net_id).\
            all()
        for p in ports:
            session.delete(p)

        session.delete(net)
        session.flush()
        return net
    except exc.NoResultFound:
        raise q_exc.NetworkNotFound(net_id=net_id)


def port_create(net_id, state=None):
    # confirm network exists
    network_get(net_id)

    session = get_session()
    with session.begin():
        port = models.Port(net_id)
        port['state'] = state or 'DOWN'
        session.add(port)
        session.flush()
        return port


def port_list(net_id):
    # confirm network exists
    network_get(net_id)
    session = get_session()
    return session.query(models.Port).\
      filter_by(network_id=net_id).\
      all()


def port_get(port_id, net_id):
    # confirm network exists
    network_get(net_id)
    session = get_session()
    try:
        return  session.query(models.Port).\
          filter_by(uuid=port_id).\
          filter_by(network_id=net_id).\
          one()
    except exc.NoResultFound:
        raise q_exc.PortNotFound(net_id=net_id, port_id=port_id)


def port_update(port_id, net_id, **kwargs):
    # confirm network exists
    network_get(net_id)
    port = port_get(port_id, net_id)
    session = get_session()
    for key in kwargs.keys():
        if key == "state":
            if kwargs[key] not in ('ACTIVE', 'DOWN'):
                raise q_exc.StateInvalid(port_state=kwargs[key])
        port[key] = kwargs[key]
    session.merge(port)
    session.flush()
    return port


def port_set_attachment(port_id, net_id, new_interface_id):
    # confirm network exists
    network_get(net_id)

    session = get_session()
    port = port_get(port_id, net_id)

    if new_interface_id != "":
        # We are setting, not clearing, the attachment-id
        if port['interface_id']:
            raise q_exc.PortInUse(net_id=net_id, port_id=port_id,
                                att_id=port['interface_id'])

        try:
            port = session.query(models.Port).\
            filter_by(interface_id=new_interface_id).\
            one()
            raise q_exc.AlreadyAttached(net_id=net_id,
                                    port_id=port_id,
                                    att_id=new_interface_id,
                                    att_port_id=port['uuid'])
        except exc.NoResultFound:
            # this is what should happen
            pass
    port.interface_id = new_interface_id
    session.merge(port)
    session.flush()
    return port


def port_unset_attachment(port_id, net_id):
    # confirm network exists
    network_get(net_id)

    session = get_session()
    port = port_get(port_id, net_id)
    port.interface_id = None
    session.merge(port)
    session.flush()


def port_destroy(port_id, net_id):
    # confirm network exists
    network_get(net_id)

    session = get_session()
    try:
        port = session.query(models.Port).\
          filter_by(uuid=port_id).\
          filter_by(network_id=net_id).\
          one()
        if port['interface_id']:
            raise q_exc.PortInUse(net_id=net_id, port_id=port_id,
                                att_id=port['interface_id'])
        session.delete(port)
        session.flush()
        return port
    except exc.NoResultFound:
        raise q_exc.PortNotFound(port_id=port_id)


def subnet_create(tenant_id, cidr, network_id):
    session = get_session()

    with session.begin():
        subnet = models.Subnet(tenant_id, cidr, network_id)
        session.add(subnet)
        session.flush()
        return subnet


def subnet_list(tenant_id):
    session = get_session()
    return session.query(models.Subnet).\
      filter_by(tenant_id=tenant_id).\
      all()


def subnet_get(subnet_id):
    session = get_session()
    try:
        return  session.query(models.Subnet).\
            filter_by(uuid=subnet_id).\
            one()
    except exc.NoResultFound, e:
        raise q_exc.SubnetNotFound(subnet_id=subnet_id)


def subnet_update(subnet_id, tenant_id, **kwargs):
    session = get_session()
    subnet = subnet_get(subnet_id)
    for key in kwargs.keys():
        if key == "cidr":
            _check_duplicate_cidr(tenant_id, kwargs[key])
        subnet[key] = kwargs[key]
    session.merge(subnet)
    session.flush()
    return subnet


def subnet_destroy(subnet_id):
    session = get_session()
    try:
        subnet = session.query(models.Subnet).\
          filter_by(uuid=subnet_id).\
          one()

        session.delete(subnet)
        session.flush()
        return subnet
    except exc.NoResultFound:
        raise q_exc.SubnetNotFound(subnet_id=subnet_id)


def subnet_set_association(subnet_id, routetable_id):
    #confirm routetable exists
    routetable_get(routetable_id)
    # confirm subnet exists
    subnet = subnet_get(subnet_id)
    id = subnet['routetable_id']

    if id:
        raise q_exc.SubnetAlreadyAssociated(subnet_id=subnet_id,
                                            routetable_id=id)

    subnet['routetable_id'] = routetable_id
    session = get_session()
    session.merge(subnet)
    session.flush()
    return subnet


def subnet_unset_association(subnet_id):
    # confirm subnet exists
    subnet = subnet_get(subnet_id)

    session = get_session()
    routetable_id = subnet['routetable_id']
    subnet['routetable_id'] = None
    session.merge(subnet)
    session.flush()
    return routetable_id


def subnet_get_association(subnet_id):
    # confirm subnet exists
    subnet = subnet_get(subnet_id)
    return subnet['routetable_id']


def routetable_create(tenant_id, **kwargs):
    session = get_session()
    label = "label-routetable-" + tenant_id
    description = "description-routetable-" + tenant_id
    for key in kwargs.keys():
        if key == "label":
            label = kwargs[key]
        if key == "description":
            description = kwargs[key]
    with session.begin():
        routetable = models.Routetable(tenant_id, label, description)
        session.add(routetable)
        session.flush()
        return routetable


def routetable_list(tenant_id):
    session = get_session()
    return session.query(models.Routetable).\
      filter_by(tenant_id=tenant_id).\
      all()


def routetable_get(routetable_id):
    session = get_session()
    try:
        return  session.query(models.Routetable).\
            filter_by(uuid=routetable_id).\
            one()
    except exc.NoResultFound, e:
        raise q_exc.RoutetableNotFound(routetable_id=routetable_id)


def routetable_update(routetable_id, tenant_id, **kwargs):
    session = get_session()
    routetable = routetable_get(routetable_id)
    for key in kwargs.keys():
        routetable[key] = kwargs[key]
    session.merge(routetable)
    session.flush()
    return routetable


def routetable_destroy(routetable_id):
    session = get_session()
    try:
        routetable = session.query(models.Routetable).\
          filter_by(uuid=routetable_id).\
          one()

        routes = session.query(models.Route).\
            filter_by(routetable_id=routetable_id).\
            all()
        for route in routes:
            session.delete(route)

        session.delete(routetable)
        session.flush()
        return routetable
    except exc.NoResultFound:
        raise q_exc.RoutetableNotFound(routetable_id=routetable_id)


def route_create(routetable_id_in, source_in, destination_in, target_in,
                 **kwargs):
    routetable_get(routetable_id_in)

    session = get_session()
    with session.begin():
        route = models.Route(routetable_id_in, source_in, destination_in,
                             target_in)
        session.add(route)
        session.flush()
        return route


def route_list(routetable_id_in):
    routetable_get(routetable_id_in)
    session = get_session()
    return session.query(models.Route).\
      filter_by(routetable_id=routetable_id_in).\
      all()


def route_get(routetable_id_in, route_id):
    routetable_get(routetable_id_in)
    session = get_session()
    try:
        return  session.query(models.Route).\
          filter_by(uuid=route_id).\
          filter_by(routetable_id=routetable_id_in).\
          one()
    except exc.NoResultFound:
        raise q_exc.RouteNotFound(routetable_id=routetable_id_in,
                                  route_in=route_in)


def route_destroy(routetable_id_in, route_id):
    routetable_get(routetable_id_in)

    session = get_session()
    try:
        route = session.query(models.Route).\
                filter_by(uuid=route_id).\
                filter_by(routetable_id=routetable_id_in).\
                one()
        session.delete(route)
        session.flush()
        return route
    except exc.NoResultFound:
        raise q_exc.RouteNotFound(routetable_id=routetable_id_in,
                                  route_id=route_id)


def route_update(routetable_id, route_id, **kwargs):
    routetable_get(routetable_id_in)
    route = route_get(routetable_id, route_id)
    session = get_session()
    for key in kwargs.keys():
        route[key] = kwargs[key]
    session.merge(route)
    session.flush()
    return route


def target_create(tag, tenant_id=None, **kwargs):
    session = get_session()
    description = "System"
    for key in kwargs.keys():
        if key == "description":
            description = kwargs[key]
    with session.begin():
        target = models.Target(tag, tenant_id, description)
        session.add(target)
        session.flush()
        return target


def target_list(tenant_id):
    session = get_session()
    return session.query(models.Target).\
      all()


def target_destroy(target_id):
    session = get_session()
    try:
        target = session.query(models.Target).\
          filter_by(uuid=target_id).\
          one()
        session.delete(target)
        session.flush()
        return target
    except exc.NoResultFound:
        raise q_exc.TargetNotFound(target_id=target_id)
