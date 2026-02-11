#!/usr/bin/env python3

"""
dhcp_server.py

DHCP server component for rouge access point
"""

import os
import sys
import time
import logging
import configparser
import subprocess
import socket
import ipaddress
from dhcppython.packet import DHCPPacket
from dhcppython.options import MessageType, SubnetMask, Router, DNSServer, IPAddressLeaseTime, ServerIdentifier
from lib.datatypes import LeaseTable

class ComponentDHCPServer(object):
    """ DHCP server object
    """

    def __init__(self, server_ip, subnet_mask, dns_server, lease_pool, lease_ttl, laddr="", lport=67, logger=None):
        """ Initialize the object
        """
        # Store arguments locally
        self.server_ip = server_ip
        self.subnet_mask = subnet_mask
        self.dns_server = dns_server
        self.lease_pool = lease_pool
        self.lease_ttl = lease_ttl
        self.laddr = laddr
        self.lport = lport
        self.logger = logger

        # Initialize lease table
        self.pool_start = ipaddress.IPv4Address(self.lease_pool[0])
        self.pool_end = ipaddress.IPv4Address(self.lease_pool[1])
        self.lease_table = LeaseTable(self.pool_start, self.pool_end, self.lease_ttl, logger=self.logger)

        # Initialize the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind((laddr, lport))

    def build_reply(self, pkt, msg_type, yiaddr):
        """ Build a reply
        """
        reply = DHCPPacket(
            op=2, # BOOTREPLY
            xid=pkt.xid,
            chaddr=pkt.chaddr,
            yiaddr=yiaddr
        )
        reply.options = [
            MessageType(msg_type),
            SubnetMask(self.subnet_mask),
            Router(self.server_ip),
            DNSServer(self.dns_server),
            IPAddressLeaseTime(self.lease_ttl),
            ServerIdentifier(self.server_ip),
        ]
        return reply

    def handle_packet(self, data):
        """ Handle the packet
        """
        pkt = DHCPPacket.from_bytes(data)
        msg = pkt.get_options(MessageType)
        if not msg:
            return None

        mac = pkt.chaddr
        req_ip_opt = pkt.get_option(RequestedIPAddress)
        requested_ip = str(req_ip_opt.value) if req_ip_opt else None

        ############################
        # HANDLE DISCOVER MESSAGES #
        ############################
        if msg.value == MessageType.DISCOVER:
            ip = self.lease_table.get_or_assign_ip(mac, requested_ip)
            if not ip:
                return None
            return self.build_reply(pkt, MessageType.OFFER, ip)

        ###########################
        # HANDLE REQUEST MESSAGES #
        ###########################
        if msg.value == MessageType.REQUEST:
            ip = self.lease_table.get_or_assign_ip(mac, requested_ip)
            if not ip:
                return None
            self.lease_table.leases[mac]["expires"] = time.time() + self.lease_ttl
            return self.build_reply(pkt, MessageType.ACK, ip)

        return None

    def start(self):
        """ Start the server
        """
        while True:
            data, _ = self.sock.recvfrom(4096)
            reply = self.handle_packet(data)
            if reply:
                self.sock.sendto(reply.to_bytes(), ("<broadcast>", self.lport))


# Begin execution
if __name__ == "__main__":
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    # Set up the logger
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger()
    logger.info(f"[DHCP Server] Initializing DHCP server component...")

    # Start the DHCP server
    lease_pool = config["DHCP"]["lease_pool"].split(",")
    server = ComponentDHCPServer(
        config["DHCP"]["server_ip"],
        config["DHCP"]["subnet_mask"],
        config["DHCP"]["dns_server"],
        lease_pool,
        config["DHCP"]["lease_ttl"],
        logger=logger
    )
    server.start() # TODO: MAKE THIS THREADED!!!!! Currently blocking SIGTERM listener

    # Run until CTRL-C recieved
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info(f"[DHCP Server] Keyboard interupt recieved, stopping DHCP server now.")
