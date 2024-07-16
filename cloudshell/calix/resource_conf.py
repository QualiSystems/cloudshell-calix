from enum import Enum

from cloudshell.shell.standards import attribute_names
from cloudshell.shell.standards.core.resource_config_entities import (
    ResourceAttrRO,
    ResourceBoolAttrRO,
)
from cloudshell.shell.standards.networking.resource_config import (
    NetworkingResourceConfig,
)


class SnmpVersion(Enum):
    V1 = "1"
    V2C = "2c"
    V3 = "3"

    @staticmethod
    def from_str(label):
        return next(
            (state for state in SnmpVersion if state.value == label), SnmpVersion.V2C
        )


class CalixNetworkingResourceConfig(NetworkingResourceConfig):
    snmp_version = SnmpVersion.from_str(
        ResourceAttrRO(
            attribute_names.SNMP_VERSION, ResourceAttrRO.NAMESPACE.SHELL_NAME
        )
    )
    enable_snmp = ResourceBoolAttrRO(
        attribute_names.ENABLE_SNMP, ResourceAttrRO.NAMESPACE.SHELL_NAME
    )
    disable_snmp = ResourceBoolAttrRO(
        attribute_names.DISABLE_SNMP, ResourceAttrRO.NAMESPACE.SHELL_NAME
    )
