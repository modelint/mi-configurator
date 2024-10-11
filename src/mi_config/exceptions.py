"""
exceptions.py – MI Config exceptions
"""

class MIConfigException(Exception):
    pass

class BadConfigData(MIConfigException):
    pass

class NonSystemInitialLayer(MIConfigException):
    pass

