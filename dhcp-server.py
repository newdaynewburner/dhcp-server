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
from lib.datatypes import DnsmasqConfigurationFileHandler
from lib.exceptions import *

class ComponentDHCPServer(object):
    """ DHCP server object
    """

    def __init__(self, config=None, logger=None):
        """ Initialize the object
        """
        self.config = config
        self.logger = logger

    def generate_configuration(self):
        """ Generate the dnsmasq configuration file
        """

        # Initialize a new DnsmasqConfigurationFileHandler object and generate the dnsmasq config file
        dnsmasq_config_file_handler = DnsmasqConfigurationFileHandler(config=self.config, logger=self.logger)
        dnsmasq_config_file = dnsmasq_config_file_handler.generate_dnsmasq_config_file()

        # Return the new filepath
        return dnsmasq_config_file

    def start(self):
        """ Start dnsmasq and monitor the process
        """
        try:
            self.dnsmasq_process = subprocess.Popen(
                [self.config["DHCP"]["dnsmasq_executable"], "-C", self.config["DHCP"]["dnsmasq_config_file"], "--keep-in-foreground"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True
        except Exception as err_msg:
            self.logger.error(f"[DHCP Server] Failed to start dnsmasq. Error message: {err_msg}")
            raise DnsmasqProcessError(f"[DHCP Server] Failed to start dnsmasq. Error message: {err_msg}")

    def stop(self):
        """ Stop dnsmasq
        """
        self.dnsmasq_process.terminate()
        try:
            self.dnsmasq_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.dnsmasq_process.kill()
            self.dnsmasq_process.wait()
        return None

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

    # Generate the dnsmasq configuration file and start the DHCP server
    dhcp_server = ComponentDHCPServer(config=config, logger=logger)
    logger.info(f"[DHCP Server] ...Generating dnsmasq configuration file at '{config['DHCP']['dnsmasq_config_file']}...")
    dnsmasq_config_file = dhcp_server.generate_configuration()
    logger.info(f"[DHCP Server] ...Bringing the DHCP server up...")
    dhcp_server.start()
    logger.info(f"[DHCP Server] ...Done! Server is up!")

    # Run until CTRL-C recieved
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info(f"[DHCP Server] Keyboard interupt recieved, stopping DHCP server now.")

