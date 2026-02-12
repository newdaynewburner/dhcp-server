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
