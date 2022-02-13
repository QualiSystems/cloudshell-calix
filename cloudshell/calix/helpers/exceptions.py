#!/usr/bin/python


class CalixBaseException(Exception):
    """Base Calix exception."""


class CalixSNMPException(CalixBaseException):
    """Calix enable/disable SNMP configuration exception."""


class CalixSaveRestoreException(CalixBaseException):
    """Calix save/restore configuration exception."""

class CalixSaveRestoreStatusException(CalixSaveRestoreException):
    """Calix save/restore configuration exception."""

class CalixConnectivityException(CalixBaseException):
    """Calix connectivity exception."""


class CalixFirmwareException(CalixBaseException):
    """Calix load firmware exception."""
