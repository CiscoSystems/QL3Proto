# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011 Cisco Systems, Inc.
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
# @author: Sumit Naiksatam, Cisco Systems, Inc.

"""
Quantum L3 Plugin API specification.

QuantumL3PluginBase provides the definition of minimum set of
methods that needs to be implemented by a Quantum L3 Plugin.
"""

import inspect
from abc import ABCMeta, abstractmethod


class QuantumL3PluginBase(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_all_subnets(self, tenant_id):
        """
        Returns a dictionary containing all
        <subnet_uuid, cidr> for
        the specified tenant.
        :returns: a list of mapping sequences with the following signature:
                     [ {'subnet_id': uuid that uniquely identifies
                                      the particular subnet,
                        'cidr': CIDR for this subnet
                       },
                       ....
                       {'subnet_id': uuid that uniquely identifies
                                      the particular subnet,
                        'cidr': CIDR for this subnet
                       }
                    ]
        :raises: None
        """
        pass

    @abstractmethod
    def create_subnet(self, tenant_id, cidr, **kwargs):
        """
        Creates a new subnet with the specified CIDR
        a symbolic name.

        :returns: a sequence of mappings with the following signature:
                    {'subnet_id': uuid that uniquely identifies the
                                     particular subnet,
                     'cidr': CIDR for this subnet
                    }
        :raises: exception.InvalidCIDR
        :raises: exception.DuplicateCIDR
        :raises: exception.NetworkNotFound
        """
        pass

    @abstractmethod
    def delete_subnet(self, tenant_id, subnet_id):
        """
        Deletes the subnet with the specified identifier
        belonging to the specified tenant.

        :returns: a sequence of mappings with the following signature:
                    {'subnet_id': uuid that uniquely identifies the
                                 particular quantum network
                    }
        :raises: exception.SubnetNotFound
        """
        pass

    @abstractmethod
    def get_subnet_details(self, tenant_id, subnet_id):
        """
        Retrieves the subnet details for a particular subnet identifier

        :returns: a sequence of mappings with the following signature:
        :returns: a sequence of mappings with the following signature:
                    {'subnet_id': uuid that uniquely identifies the
                                     particular subnet,
                     'cidr': CIDR for this subnet,
                     'network_id': network identifier associated with
                                   this subnet
                    }
        :raises: exception.SubnetNotFound
        """
        pass

    @abstractmethod
    def update_subnet(self, tenant_id, subnet_id, **kwargs):
        """
        Updates the attributes of a particular subnet

        :returns: a sequence of mappings with the following signature:
                    {'subnet_id': uuid that uniquely identifies the
                                     particular subnet,
                     'cidr': CIDR for this subnet
                    }
        :raises: exception.SubnetNotFound
        :raises: exception.InvalidCIDR
        :raises: exception.DuplicateCIDR
        :raises: exception.NetworkNotFound
        """
        pass

    @abstractmethod
    def get_all_routetables(self, tenant_id):
        """
        Returns a dictionary containing all
        <routetable_uuid> for
        the specified tenant.
        :returns: a list of mapping sequences with the following signature:
                     [ {'routetable_id': uuid that uniquely identifies
                                      the particular routetable
                       },
                       ....
                       {'routetable_id': uuid that uniquely identifies
                                      the particular routetable
                       }
                    ]
        :raises: None
        """
        pass

    @abstractmethod
    def create_routetable(self, tenant_id, **kwargs):
        """
        Creates a new routetable

        :returns: a sequence of mappings with the following signature:
                    {'routetable_id': uuid that uniquely identifies the
                                     particular routetable,
                    }
        :raises: None
        """
        pass

    @abstractmethod
    def delete_routetable(self, tenant_id, routetable_id):
        """
        Deletes the routetable with the specified identifier
        belonging to the specified tenant.

        :returns: a sequence of mappings with the following signature:
                    {'routetable_id': uuid that uniquely identifies the
                                 particular quantum network
                    }
        :raises: exception.RoutetableNotFound
        """
        pass

    @abstractmethod
    def get_routetable_details(self, tenant_id, routetable_id):
        """
        Retrieves the routetable details for a particular routetable identifier

        :returns: a sequence of mappings with the following signature:
                    {'routetable_id': uuid that uniquely identifies the
                                     particular routetable,
                     'label': user defined label,
                     'description': user defined description
                    }
        :raises: exception.RoutetableNotFound
        """
        pass

    @abstractmethod
    def update_routetable(self, tenant_id, routetable_id, **kwargs):
        """
        Updates the attributes of a particular routetable

        :returns: a sequence of mappings with the following signature:
                    {'routetable_id': uuid that uniquely identifies the
                                     particular routetable,
                    }
        :raises: exception.RoutetableNotFound
        :raises: exception.NetworkNotFound
        """
        pass

    @abstractmethod
    def get_all_routes(self, tenant_id, routetable_id):
        """
        Returns a dictionary containing all
        <source, destination, target> for
        the specified tenant.
        :returns: a list of mapping sequences with the following signature:
                     [ {'source'': source identifier
                        'destination': destination identifier
                        'target': target identifier
                       },
                       ....
                       {'source': source identifier
                        'destination': destination identifier
                        'target': target identifier
                       }
                    ]
        :raises: exception.RoutetableNotFound
        """
        pass

    @abstractmethod
    def create_route(self, tenant_id, routetable_id, source, destination,
                     target, **kwargs):
        """
        Creates a new route

        :returns: a sequence of mappings with the following signature:
                    {'routetable_id': uuid that uniquely identifies the
                                      routetable,
                     'source': source identifier,
                     'destination': destination indentifier,
                     'target': target identifier,
                    }
        :raises: exception.RoutetableNotFound
        :raises: exception.RouteSourceInvalid
        :raises: exception.RouteDestinationInvalid
        :raises: exception.RouteTargetInvalid
        """
        pass

    @abstractmethod
    def delete_route(self, tenant_id, routetable_id, route_id):
        """
        Deletes the route with the specified source and destination

        :returns: a sequence of mappings with the following signature:
                    {'routetable_id': uuid that uniquely identifies the
                                 particular quantum routetable,
                     'route_id': uuid that uniquely identifies the route
                    }
        :raises: exception.RoutetableNotFound
        :raises: exception.RouteNotFound
        """
        pass

    @abstractmethod
    def get_route_details(self, tenant_id, routetable_id, route_id):
        """
        Retrieves the route details for a particular route identifier

        :returns: a sequence of mappings with the following signature:
                    {'routetable_id': uuid that uniquely identifies the
                                     particular routetable,
                     'route_id': uuid that uniquely identifies the route
                     'source': source identifier,
                     'destination': destination indentifier,
                     'target': target identifier,
                    }
        :raises: exception.RoutetableNotFound
        :raises: exception.RouteNotFound
        """
        pass

    @abstractmethod
    def get_all_targets(self, tenant_id, routetable_id):
        """
        Returns all the targets available for this tenant_id
        <tag, description> for
        :returns: a list of mapping sequences with the following signature:
                     [ {'tag'': target identifier
                        'description': information about the tag
                       },
                       ....
                       {'tag'': target identifier
                        'description': information about the tag
                       },
                    ]
        :raises: exception.RoutetableNotFound
        """
        pass

    def get_subnet_association(self, tenant_id, subnet_id):
        """
        retrieves the routetable associated with a subnet
        :returns: Dictionary with the associated routetable_id
        :raises: exception.SubnetNotFound
        """

    def associate_subnet(self, tenant_id, subnet_id, routetable_id):
        """
        associates a subnet to a routetable
        :returns: nothing
        :raises: exception.SubnetNotFound
        :raises: exception.RoutetableNotFound
        :raises: exception.SubnetAlreadyAttached
        """

    def disassociate_subnet(self, request, tenant_id, subnet_id):
        """
        disassociates a subnet from a routetable
        :returns: nothing
        :raises: exception.SubnetNotFound
        """

    @classmethod
    def __subclasshook__(cls, klass):
        """
        The __subclasshook__ method is a class method
        that will be called everytime a class is tested
        using issubclass(klass, Plugin).
        In that case, it will check that every method
        marked with the abstractmethod decorator is
        provided by the plugin class.
        """
        if cls is QuantumL3PluginBase:
            for method in cls.__abstractmethods__:
                method_ok = False
                for base in klass.__mro__:
                    if method in base.__dict__:
                        fn_obj = base.__dict__[method]
                        if inspect.isfunction(fn_obj):
                            abstract_fn_obj = cls.__dict__[method]
                            arg_count = fn_obj.func_code.co_argcount
                            expected_arg_count = \
                                abstract_fn_obj.func_code.co_argcount
                            method_ok = arg_count == expected_arg_count
                if method_ok:
                    continue
                return NotImplemented
            return True
        return NotImplemented
