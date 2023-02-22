#!/usr/bin/python

from cloudshell.shell.flows.configuration.basic_flow import AbstractConfigurationFlow
from cloudshell.shell.flows.utils.networking_utils import UrlParser

from cloudshell.calix.command_actions.save_restore_actions import SaveRestoreActions
from cloudshell.calix.helpers.exceptions import CalixSaveRestoreException


class CalixConfigurationFlow(AbstractConfigurationFlow):
    DEFAULT_CONFIG_NAME = "quali-configuration-backup"
    DEFAULT_LOCAL_PATH = "config"
    STARTUP_CONFIG = "startup-config"
    REMOTE_PROTOCOLS = ["ftp", "tftp", "scp"]
    BACKUP_STARTUP_CONFIG = "quali-startup-backup"

    def __init__(self, cli_handler, resource_config, logger):
        super().__init__(logger, resource_config)
        self._cli_handler = cli_handler

    @property
    def _file_system(self):
        """Determine device file system type."""
        return "config"

    def _save_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """Execute flow which save selected file to the provided destination.

        :param folder_path: destination path where file will be saved
        :param configuration_type: source file, which will be saved
        :param vrf_management_name: Virtual Routing and Forwarding Name
        :return: saved configuration file name
        """
        if not configuration_type.endswith("-config"):
            configuration_type += "-config"

        if configuration_type not in ["running-config", "startup-config"]:
            raise CalixSaveRestoreException(
                "Device doesn't support saving '{}' configuration type".format(
                    configuration_type
                ),
            )

        url = UrlParser().parse_url(folder_path)
        scheme = url.get("scheme")
        avail_protocols = self.REMOTE_PROTOCOLS + [self._file_system]
        if scheme not in avail_protocols:
            raise CalixSaveRestoreException(
                f"Unsupported protocol type {scheme}."
                f"Available protocols: {avail_protocols}"
            )

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as enable_session:
            save_action = SaveRestoreActions(enable_session, self._logger)
            filename = url.get("filename", self.DEFAULT_CONFIG_NAME)

            save_action.copy_configuration(
                src_file=configuration_type, dst_file=filename
            )

            if scheme in self.REMOTE_PROTOCOLS:
                save_action.save_configuration_to_remote(
                    folder=self._file_system,
                    filename=filename,
                    destination_url=folder_path,
                    vrf=vrf_management_name,
                )
                try:
                    save_action.check_file_transfer_status()
                finally:
                    save_action.delete_local_config_file(filename)

    def _restore_flow(
        self, path, configuration_type, restore_method, vrf_management_name
    ):
        """Execute flow which save selected file to the provided destination.

        :param path: the path to the configuration file, including the configuration
            file name
        :param restore_method: the restore method to use when restoring the
            configuration file. Possible Values are append and override
        :param configuration_type: the configuration type to restore.
            Possible values are startup and running
        :param vrf_management_name: Virtual Routing and Forwarding Name
        """
        configuration_type = configuration_type.lower()
        if configuration_type.lower() not in ["running", "startup"]:
            raise CalixSaveRestoreException(
                "Device doesn't support restoring '{}' configuration type".format(
                    configuration_type
                ),
            )

        config_type = configuration_type.lower()
        if not config_type.endswith("-config"):
            config_type += "-config"

        if not restore_method:
            restore_method = "override"

        url = UrlParser().parse_url(path)
        scheme = url.get("scheme")
        avail_protocols = self.REMOTE_PROTOCOLS + [self._file_system]
        if scheme not in avail_protocols:
            raise CalixSaveRestoreException(
                f"Unsupported protocol type {scheme}."
                f"Available protocols: {avail_protocols}"
            )

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as enable_session:
            save_action = SaveRestoreActions(enable_session, self._logger)
            filename = url.get("filename", self.DEFAULT_CONFIG_NAME)
            if scheme in self.REMOTE_PROTOCOLS:
                save_action.load_configuration_from_remote(
                    folder=self._file_system,
                    url=path,
                    filename=filename,
                    vrf=vrf_management_name,
                )
            save_action.check_file_transfer_status()

            filename = url.get("filename", self.DEFAULT_CONFIG_NAME)
            if restore_method.lower() == "override" and "running" in config_type:
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
                save_action.copy_configuration(filename, config_type)
            save_action.delete_local_config_file(filename)
            if "running" in config_type:
                save_action.accept_changes()
