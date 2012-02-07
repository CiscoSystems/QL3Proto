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
# Based on the models.py used for Quantum L2
# @author: Sumit Naiksatam, Cisco Systems, Inc.

import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, object_mapper

from quantum.api import api_common as common

BASE = declarative_base()


class QuantumBase(object):
    """Base class for Quantum Models."""

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __iter__(self):
        self._i = iter(object_mapper(self).columns)
        return self

    def next(self):
        n = self._i.next().name
        return n, getattr(self, n)

    def update(self, values):
        """Make the model object behave like a dict"""
        for k, v in values.iteritems():
            setattr(self, k, v)

    def iteritems(self):
        """Make the model object behave like a dict.
        Includes attributes from joins."""
        local = dict(self)
        joined = dict([(k, v) for k, v in self.__dict__.iteritems()
                      if not k[0] == '_'])
        local.update(joined)
        return local.iteritems()


class Subnet(BASE, QuantumBase):
    """Represents a quantum subnet"""
    __tablename__ = 'subnets'

    uuid = Column(String(255), primary_key=True)
    tenant_id = Column(String(255), nullable=False)
    cidr = Column(String(255), nullable=False)
    network_id = Column(String(255), nullable=True)
    routetable_id = Column(String(255), ForeignKey("routetables.uuid"),
                        nullable=True)

    def __init__(self, tenant_id, cidr, network_id):
        self.uuid = str(uuid.uuid4())
        self.tenant_id = tenant_id
        self.cidr = cidr
        self.network_id = network_id

    def __repr__(self):
        return "<Network(%s,%s,%s,%s)>" % \
          (self.uuid, self.cidr, self.network_id, self.tenant_id)


class Route(BASE, QuantumBase):
    """Represents a route in a Routetable"""
    __tablename__ = 'routes'

    uuid = Column(String(255), primary_key=True)
    routetable_id = Column(String(255), ForeignKey("routetables.uuid"),
                        nullable=False)
    source = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    target = Column(String(255), nullable=False)

    def __init__(self, routetable_id, source, destination, target):
        self.uuid = str(uuid.uuid4())
        self.routetable_id = routetable_id
        self.source = source
        self.destination = destination
        self.target = target

    def __repr__(self):
        return "<Route(%s,%s,%s,%s,%s)>" % (self.uuid, self.routetable_id,
                                           self.source, self.destination,
                                           self.target)


class Routetable(BASE, QuantumBase):
    """Represents a Routetable"""
    __tablename__ = 'routetables'

    uuid = Column(String(255), primary_key=True)
    tenant_id = Column(String(255), nullable=False)
    label = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    routes = relation(Route, order_by=Route.uuid, backref="routetable")
    subnets = relation(Subnet, order_by=Subnet.uuid, backref="subnet")

    def __init__(self, tenant_id, label=None, description=None):
        self.uuid = str(uuid.uuid4())
        self.tenant_id = tenant_id
        self.label = label
        self.description = description

    def __repr__(self):
        return "<Routetable(%s,%s)>" % \
          (self.uuid, self.tenant_id)


class Target(BASE, QuantumBase):
    """Represents Target identifiers"""
    __tablename__ = 'targets'

    uuid = Column(String(255), primary_key=True)
    tenant_id = Column(String(255), nullable=True)
    tag = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

    def __init__(self, tag, tenant_id=None, description=None):
        self.uuid = str(uuid.uuid4())
        self.tenant_id = tenant_id
        self.tag = tag
        self.description = description

    def __repr__(self):
        return "<Target(%s,%s)>" % \
          (self.tag, self.description)
