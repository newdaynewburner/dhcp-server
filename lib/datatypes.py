"""
lib/datatypes.py

Custom datatype definitions
"""

import os
import sys
import ipaddress

class LeaseTable(object):
    """ DHCP leasing table
    """

    def __init__(self, pool_start, pool_end, lease_ttl, logger=None):
        """ Initialize the object
        """
        self.logger = logger
        self.pool_start = pool_start
        self.pool_end = pool_end
        self.lease_ttl = lease_ttl
        self.leases = {}

    def cleanup_expired(self):
        """ Clean up expired leases
        """
        now = time.time()
        self.leases = {
            mac: lease
            for mac, lease in self.leases.items()
            if lease["expires"] > now
        }

    def ip_in_use(self, ip):
        """ Check if an IP is in use or not
        """
        for mac in self.leases.keys():
            if ip == self.leases[mac]["ip"]:
                return True
        return False

    def allocate_ip(self):
        """ Return an unused IP address
        """
        for i in range(int(self.pool_start), int(self.pool_end) + 1):
            ip = str(ipaddress.IPv4Address(i))
            if not self.ip_in_use(ip):
                return ip
        return None

    def get_or_assign_ip(self, mac, requested_ip=None):
        """ Get or assign an IP address
        """
        # Remove expired leases
        self.cleanup_expired()

        # Return IP for existing mac
        if mac in self.leases:
            return self.leases[mac]["ip"]

        # Check if the requested IP is in use and allocate one if so
        if not self.ip_in_use(requested_ip):
            ip = requested_ip
        else:
            ip = self.allocate_ip()

        # Update the lease table
        self.leases[mac] = {
            "ip": ip,
            "expires": time.time() + self.lease_ttl
        }
        return ip
