#!/usr/bin/python

from cloudshell.calix.autoload.snmp_system_info import (
    CalixSnmpSystemInfo,
)
from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload


class CalixGenericSNMPAutoload(GenericSNMPAutoload):
    def __init__(self, snmp_handler, logger):
        super().__init__(snmp_handler, logger)

    @property
    def system_info_service(self):
        if not self._system_info:
            self._system_info = CalixSnmpSystemInfo(self.snmp_handler, self.logger)
        return self._system_info
