# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011, Cisco Systems, Inc.
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
# @author: Rohit Agarwalla, Cisco Systems, Inc.
# @author: Sumit Naiksatam, Cisco Systems, Inc.


"""Implements iptables rules using linux utilities."""


import logging
import subprocess

from quantum.plugins.l3.utils import utils as util


LOG = logging.getLogger(__name__)


class IptablesRule(object):
    """An iptables rule.
    """

    def __init__(self, chain, rule):
        self.chain = chain
        self.rule = rule

    def __eq__(self, other):
        return ((self.chain == other.chain) and
                (self.rule == other.rule))

    def __ne__(self, other):
        return not self == other


class IptablesTable(object):
    """An iptables table."""

    def __init__(self):
        self.chains = set()
        self.rules = []

    def add_chain(self, name):
        """Add chain to a table"""
        if name in self.chains:
            return
        command_string = ["iptables", "-N", name]
        util.execute_command_string(command_string)
        self.chains.add(name)
        # TODO (Sumit): Also need to add this rule to the FORWARD table
        # sudo iptables -I FORWARD 1 -j l3-linux-FORWARD

    def add_chain_restore(self, name):
        """Add chain only to a table"""
        self.chains.add(name)

    def remove_chain(self, name):
        """Remove chain from a table"""
        chain_rules = filter(lambda r: r.chain == name, self.rules)
        for rule_obj in chain_rules:
            command_string = ["iptables", "-D", name]
            command_string = util.extend_string_list(command_string,
                                                     rule_obj.rule)
            util.execute_command_string(command_string)
        self.rules = filter(lambda r: r.chain != name, self.rules)

        jump_snippet = '-j %s' % (name,)
        command_string = ["iptables", "-D", "FORWARD"]
        command_string = util.extend_string_list(command_string, jump_snippet)
        util.execute_command_string(command_string)
        self.rules = filter(lambda r: jump_snippet not in r.rule, self.rules)

        command_string = ["iptables", "-X", name]
        util.execute_command_string(command_string)
        self.chains.remove(name)

    def add_rule(self, chain, rule, insert=False, pos=None):
        """Add a rule to a chain
        """
        if not insert:
            command_string = ["iptables", "-A", chain]
        else:
            command_string = ["iptables", "-I", chain, pos]
        command_string = util.extend_string_list(command_string, rule)
        rule = ''.join(rule.split())
        if IptablesRule(chain, rule) in self.rules:
            return
        util.execute_command_string(command_string)
        self.rules.append(IptablesRule(chain, rule))

    def add_rule_restore(self, chain, rule):
        """Add only a rule to a chain"""
        rule = ''.join(rule.split())
        self.rules.append(IptablesRule(chain, rule))

    def remove_rule(self, chain, rule):
        """Remove a rule from a chain.
        """
        command_string = ["iptables", "-D", chain]
        command_string = util.extend_string_list(command_string, rule)
        util.execute_command_string(command_string)
        rule = ''.join(rule.split())
        # TODO (Sumit): The following raises and exception if no rule
        # is present need to handle this properly in such cases as well
        try:
            self.rules.remove(IptablesRule(chain, rule))
        except Exception as exc:
            LOG.warning("Failed to remove rule:%s from chain:%s" % (rule,
                                                                    chain))

    def print_rules_chain(self):
        """Print all the rules in a chain"""
        for rule_obj in self.rules:
            """TODO(Rohit):Replace with LOG"""
            print rule_obj.chain, " ", rule_obj.rule


class IptablesManager(object):
    """Wrapper for iptables.
    """

    def __init__(self):
        self.ipv4 = {'filter': IptablesTable(),
                     'nat': IptablesTable()}

    def subnet_public_accept(self, subnet, public_interface):
        """Allow subnet to internet traffic
        """
        # TODO (Sumit): This probably needs to be:
        # sudo iptables -I l3-linux-FORWARD 1 -s cidr  -i bridge_dev_name
        # -o public_interface -j ACCEPT
        self.ipv4['filter'].add_rule("l3-linux-FORWARD", \
                                     "-s %(subnet)s -o %(p_int)s" \
                                     " -j ACCEPT" % {'subnet': subnet,\
                                     'p_int': public_interface},\
                                     True, "1")

    def subnet_public_drop(self, subnet, public_interface):
        """Allow subnet to internet traffic
        """
        # TODO (Sumit): This probably needs to be:
        # sudo iptables -I l3-linux-FORWARD 1 -s cidr  -i bridge_dev_name
        # -o public_interface -j ACCEPT
        self.ipv4['filter'].remove_rule("l3-linux-FORWARD", \
                                     "-s %(subnet)s -o %(p_int)s" \
                                     " -j ACCEPT" % {'subnet': subnet,\
                                     'p_int': public_interface})

    def subnet_drop_all(self, subnet):
        """Deny subnet traffic
        """
        self.ipv4['filter'].add_chain("l3-linux-FORWARD")
        self.ipv4['filter'].add_rule("FORWARD", "-j l3-linux-FORWARD", \
                                      True, "1")
        self.ipv4['filter'].add_rule("l3-linux-FORWARD", \
                                     "-s %(subnet)s ! -d %(subnet)s" \
                                     " -j DROP" % {'subnet': subnet})

    def subnet_accept_all(self, subnet):
        """Allow subnet traffic
        """
        self.ipv4['filter'].remove_rule("l3-linux-FORWARD", \
                                     "-s %(subnet)s ! -d %(subnet)s" \
                                     " -j DROP" % {'subnet': subnet})

    def inter_subnet_accept(self, source_subnet, destination_subnet):
        """Allow source subnet to destination subnet traffic
        """
        self.ipv4['filter'].add_rule("l3-linux-FORWARD", \
                                     "-s %(source)s -d %(dest)s" \
                                     " -j ACCEPT" % {'source': source_subnet,\
                                     'dest': destination_subnet}, True, "1")

        self.ipv4['filter'].add_rule("l3-linux-FORWARD", \
                                     "-d %(source)s " \
                                     "-m state --state RELATED,ESTABLISHED "
                                     "-j ACCEPT" % {'source': source_subnet},\
                                     True, "1")

    def inter_subnet_drop(self, source_subnet, destination_subnet):
        """Drop source subnet to destination subnet traffic
        """
        self.ipv4['filter'].remove_rule("l3-linux-FORWARD", \
                                     "-s %(source)s -d %(dest)s " \
                                     "-j ACCEPT" % {'source': source_subnet,\
                                     'dest': destination_subnet})

        self.ipv4['filter'].remove_rule("l3-linux-FORWARD", \
                                     "-d %(source)s " \
                                     "-m state --state RELATED,ESTABLISHED "
                                     "-j ACCEPT" % {'source': source_subnet})

    def add_snat_rule(self, cidr, public_ip):
        """SNAT rule for outgoing public traffic"""
        self.ipv4['nat'].add_chain("nova-network-snat")
        self.ipv4['nat'].add_rule("nova-network-snat", \
                                   "-s %s -j SNAT --to-source %s" % \
                                   (cidr, public_ip))

    def remove_snat_rule(self, cidr, public_ip):
        """SNAT rule for outgoing public traffic"""
        self.ipv4['nat'].remove_rule("nova-network-snat", \
                                   "-s %s -j SNAT --to-source %s" % \
                                   (cidr, public_ip))

    def add_init_gateway(self, bridge_interface, gateway):
        """Allow/Deny incoming and outgoing traffic on bridge interface
           based on gateway"""
        self.ipv4['filter'].add_chain("nova-network-FORWARD")
        if gateway:
            self.ipv4['filter'].add_rule("nova-network-FORWARD",
                                     "--in-interface %s -j ACCEPT" % \
                                     bridge_interface)
            self.ipv4['filter'].add_rule("nova-network-FORWARD",
                                     "--out-interface %s -j ACCEPT" % \
                                     bridge_interface)
        else:
            self.ipv4['filter'].add_rule("nova-network-FORWARD",
                                     "--in-interface %s -j DROP" % \
                                     bridge_interface)
            self.ipv4['filter'].add_rule("nova-network-FORWARD",
                                     "--out-interface %s -j DROP" % \
                                     bridge_interface)

    def remove_init_gateway(self, bridge_interface, gateway):
        if gateway:
            self.ipv4['filter'].remove_rule("nova-network-FORWARD",
                                     "--in-interface %s -j ACCEPT" % \
                                     bridge_interface)
            self.ipv4['filter'].remove_rule("nova-network-FORWARD",
                                     "--out-interface %s -j ACCEPT" % \
                                     bridge_interface)
        else:
            self.ipv4['filter'].remove_rule("nova-network-FORWARD",
                                     "--in-interface %s -j DROP" % \
                                     bridge_interface)
            self.ipv4['filter'].remove_rule("nova-network-FORWARD",
                                     "--out-interface %s -j DROP" % \
                                     bridge_interface)

    def clear_all(self, chain_name):
        """Remove chain and all rules in that chain
        """
        self.ipv4['filter'].remove_chain(chain_name)

    def initialize(self):
        """Remove any traces of old chain
        """
        LOG.debug("inside iptables initialize()")
        command_string = ["sudo", "iptables", "--list", "l3-linux-FORWARD"]
        cmd_output = util.execute_command_string(command_string)
        if not cmd_output:
            self.ipv4['filter'].add_chain("l3-linux-FORWARD")
            return
        command_string = ["iptables", "-S", "-t", "filter"]
        cmd_output = util.execute_command_string(command_string)
        if cmd_output:
            stale_rule_list = [rules for rules in cmd_output.splitlines() \
                               if "l3-linux-FORWARD" in rules]
            for rule in reversed(stale_rule_list):
                rule_string = rule[3:]
                if rule[1] == "A":
                    command_string = ["iptables", "-D"]
                elif rule[1] == "N":
                    command_string = ["iptables", "-X"]
                command_string = util.extend_string_list(command_string, \
                                                         rule_string)
                command_string = filter(None, command_string)
                util.execute_command_string(command_string)

    def restore(self):
        """Restore data structures after restart
        """
        command_string = ["iptables", "-S", "-t", "filter"]
        cmd_output = util.execute_command_string(command_string)
        restore_rule_list = [rules for rules in cmd_output.splitlines() \
                           if "l3-linux-FORWARD" in rules]

        for rule in restore_rule_list:
            rule_string = rule[3:]
            if rule[1] == "A":
                rule_string = filter(None, rule_string)
                new_rule_string = rule_string[rule_string.find(" ") + 1:]
                self.ipv4['filter'].add_rule_restore(\
                                         "l3-linux-FORWARD", new_rule_string)
            elif rule[1] == "N":
                self.ipv4['filter'].add_chain_restore("l3-linux-FORWARD")
        self.ipv4['filter'].print_rules_chain()


if __name__ == '__main__':
    iptables_manager = IptablesManager()
    iptables_manager.initialize()

    option = raw_input("Enter q/c/d/a")
    while (option != "q"):
        if (option == "c"):
            iptables_manager.clear_all("l3-linux-FORWARD")
        elif (option == "d"):
            iptables_manager.inter_subnet_drop("10.10.14.0/24",\
                                               "10.10.15.0/24")
        elif (option == "a"):
            iptables_manager.inter_subnet_accept("10.10.14.0/24",\
                                                 "10.10.15.0/24")
        else:
            print "Invalid option"
        option = raw_input("Enter q/c/d/a")
