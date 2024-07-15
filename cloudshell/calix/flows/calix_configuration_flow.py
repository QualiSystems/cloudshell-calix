from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from cloudshell.shell.flows.configuration.basic_flow import (
    AbstractConfigurationFlow,
    ConfigurationType,
    RestoreMethod,
)

from cloudshell.calix.command_actions.save_restore_actions import SaveRestoreActions
from cloudshell.calix.helpers.exceptions import CalixSaveRestoreException

if TYPE_CHECKING:
    from typing import Union

    from cloudshell.shell.flows.utils.url import BasicLocalUrl, RemoteURL
    from cloudshell.shell.standards.networking.resource_config import (
        NetworkingResourceConfig,
    )

    from ..cli.calix_cli_configurator import CalixCliConfigurator

    Url = Union[RemoteURL, BasicLocalUrl]


logger = logging.getLogger(__name__)


class CalixConfigurationFlow(AbstractConfigurationFlow):
    SUPPORTED_CONFIGURATION_TYPES: set[ConfigurationType] = {
        ConfigurationType.RUNNING,
        ConfigurationType.STARTUP,
    }
    SUPPORTED_RESTORE_METHODS: set[RestoreMethod] = {
        RestoreMethod.OVERRIDE,
        RestoreMethod.APPEND,
    }
    DEFAULT_CONFIG_NAME = "quali-configuration-backup"
    DEFAULT_LOCAL_PATH = "config"
    STARTUP_CONFIG = "startup-config"
    REMOTE_PROTOCOLS = ["ftp", "tftp", "scp"]
    BACKUP_STARTUP_CONFIG = "quali-startup-backup"

    def __init__(
        self,
        resource_config: NetworkingResourceConfig,
        cli_configurator: CalixCliConfigurator,
    ):
        super().__init__(resource_config)
        self.cli_configurator = cli_configurator

    @property
    def file_system(self) -> str:
        """Determine device file system type."""
        return "config"

    def _save_flow(
        self,
        file_dst_url: Url,
        configuration_type: ConfigurationType,
        vrf_management_name: str | None,
    ) -> None:
        """Execute flow which save selected file to the provided destination."""
        avail_protocols = self.REMOTE_PROTOCOLS + [self.file_system]
        if file_dst_url.scheme not in avail_protocols:
            raise CalixSaveRestoreException(
                f"Unsupported protocol type {file_dst_url.scheme}."
                f"Available protocols: {avail_protocols}"
            )

        with self.cli_configurator.enable_mode_service() as cli_service:
            save_action = SaveRestoreActions(cli_service)
            filename = file_dst_url.filename or self.DEFAULT_CONFIG_NAME

            save_action.copy_configuration(
                src_file=configuration_type.value, dst_file=filename
            )

            if file_dst_url.scheme in self.REMOTE_PROTOCOLS:
                save_action.save_configuration_to_remote(
                    folder=self.file_system,
                    filename=filename,
                    destination_url=str(file_dst_url),
                    vrf=vrf_management_name,
                )
                try:
                    save_action.check_file_transfer_status()
                finally:
                    save_action.delete_local_config_file(filename)

    def _restore_flow(
        self,
        config_path: Url,
        configuration_type: ConfigurationType,
        restore_method: RestoreMethod,
        vrf_management_name: str | None,
    ) -> None:
        """Execute flow which save selected file to the provided destination."""
        avail_protocols = self.REMOTE_PROTOCOLS + [self.file_system]
        if config_path not in avail_protocols:
            raise CalixSaveRestoreException(
                f"Unsupported protocol type {config_path}."
                f"Available protocols: {avail_protocols}"
            )

        with self.cli_configurator.enable_mode_service() as cli_service:
            save_action = SaveRestoreActions(cli_service)
            filename = config_path.filename or self.DEFAULT_CONFIG_NAME
            if config_path in self.REMOTE_PROTOCOLS:
                save_action.load_configuration_from_remote(
                    folder=self.file_system,
                    url=str(config_path),
                    filename=filename,
                    vrf=vrf_management_name,
                )
            save_action.check_file_transfer_status()

            if (
                restore_method == RestoreMethod.OVERRIDE
                and configuration_type == ConfigurationType.RUNNING
            ):
                save_action.copy_configuration(
                    self.STARTUP_CONFIG, self.BACKUP_STARTUP_CONFIG
                )
                save_action.copy_configuration(filename, self.STARTUP_CONFIG)
                save_action.reload_device(600)
                save_action.copy_configuration(
                    self.BACKUP_STARTUP_CONFIG, self.STARTUP_CONFIG
                )
                save_action.delete_local_config_file(self.BACKUP_STARTUP_CONFIG)
            else:
                save_action.copy_configuration(filename, configuration_type.value)
            save_action.delete_local_config_file(filename)
            if configuration_type == ConfigurationType.RUNNING:
                save_action.accept_changes()
