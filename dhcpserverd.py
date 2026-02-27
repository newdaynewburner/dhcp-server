#!/usr/bin/env python3

"""
dhcp_server.py

DHCP server component for rouge access point
"""

import os
import sys
import logging
import configparser
from lib import api

def main(config, logger):
    """ Main function. Controls program execution
    """
    logger.info(f"Starting the DHCP server service. DBus API is com.dhcpserver.DHCPServer")
    try:
        api.init_dbus_api()
    except KeyboardInterrupt:
        logger.info(f"Keyboard interrupt recieved, stopping DHCP server service now")
        return None

# Begin execution
if __name__ == "__main__":
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    # Set up the logger
    if bool(config["DHCP"]["log_file"]):
        log_file = config["DHCP"]["log_file"]
        if "~" in log_file:
            log_file = os.path.expanduser(log_file)
        if not os.path.isdir(os.path.split(log_file)[0]):
            os.makedirs(os.path.split(log_file)[0])
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - [DHCP Server] %(message)s",
            filename=log_file
        )
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - [DHCP Server] %(message)s"
        )
    logger = logging.getLogger()

    # Enter the main function
    main(config, logger)
