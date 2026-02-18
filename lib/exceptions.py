"""
lib/exceptions.py

Custom exception definitions
"""

import warnings

class StaticLeaseFileError(Exception):
    """ Called when an error related to the static lease file occurs
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DnsmasqConfigFileWriteError(Exception):
    """ Called when an error related to the static lease file occurs
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class StateChangeError(Exception):
    """ Raised when starting, stopping, or restarting the DHCP server fails
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ConfigurationError(Exception):
    """ Raised when an error occurs reading or writing a configuration file
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
