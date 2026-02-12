"""
lib/datatypes.py

Custom datatype definitions
"""

import os
import sys
import ipaddress
from . import exceptions

class DnsmasqConfigurationFileHandler(object):
    """ Contains methods for dynamically generating the configuration
    file for dnsmasq
    """

    def __init__(self, config=None, logger=None):
        """ Initialize the object
        """

        # Store arguments locally
        self.config = config
        self.logger = logger

        # Initialize attributes
        self.dnsmasq_settings = []

        # Create the directory for the dnsmasq configuration file if it does not already exist
        if not os.path.isdir(os.path.split(self.config["DHCP"]["dnsmasq_config_file"])[0]):
            os.makedirs(os.path.split(self.config["DHCP"]["dnsmasq_config_file"])[0])

    def generate_dnsmasq_config_file(self):
        """ Dynamically generate the dnsmasq configuration file
        """

        # Initialize a list to hold configuration file settings
        settings = []

        # Build the IP address pool
        lease_pool = f"{self.config['DHCP']['pool_start']},{self.config['DHCP']['pool_end']},{self.config['DHCP']['lease_time']}"

        # Generate the base settings
        for setting in [
            f"interface={self.config['DHCP']['interface']}",
            f"bind-interfaces",
            #f"port=0",
            #f"log-dhcp",
            #f"dhcp-leasefile={self.config['DHCP']['dnsmasq_lease_file']}",
            #f"dhcp-option=3,{self.config['DHCP']['gateway']}",
            f"server={self.config['DHCP']['dns_server']}",
            f"dhcp-range={self.config['DHCP']['pool_start']},{self.config['DHCP']['pool_end']},{self.config['DHCP']['lease_time']}"
        ]:
            settings.append(setting)

        # Generate the dnsmasq dhcp-script setting
        if self.config["DHCP"]["dnsmasq_dhcp_script"]:
            settings.append(f"dhcp-script={self.config['DHCP']['dnsmasq_dhcp_script']}")

        # Generate the static lease settings
        if self.config["DHCP"]["static_lease_file"]:
            if not os.path.isfile(self.config["DHCP"]["static_lease_file"]):
                raise exceptions.StaticLeaseFileError(f"Specified static lease file does not exist!")
            with open(self.config["DHCP"]["static_lease_file"], "r") as f:
                static_lease_settings = []
                for static_lease in f.readlines():
                    parts = static_lease.split(",")
                    if len(parts) == 2:
                        static_lease_settings.append(f"dhcp-host={parts[0]},{parts[1]}")
                    elif len(parts) == 3:
                        static_lease_settings.append(f"dhcp-host={parts[0]},{parts[1]},{parts[2]}")
                    else:
                        raise exceptions.StaticLeaseFileError(f"Bad line in static lease file!")
            for static_lease_setting in static_lease_settings:
                settings.append(static_lease_setting)

        # Write the settings to the specified dnsmasq configuration file
        with open(self.config["DHCP"]["dnsmasq_config_file"], "w") as dnsmasq_config:
            for line in settings:
                dnsmasq_config.write(line + "\n")

        # Verify the file was written and return its filepath
        self.dnsmasq_settings = settings
        if not os.path.isfile(self.config["DHCP"]["dnsmasq_config_file"]):
            raise Exception(f"Error writing dnsmasq configuration file to disk! File not found on filesystem!")
        return self.config["DHCP"]["dnsmasq_config_file"]
