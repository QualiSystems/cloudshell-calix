from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from attrs import define
from retrying import retry

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.session.session_exceptions import SessionException
from cloudshell.cli.types import T_ACTION_MAP, T_ERROR_MAP

from cloudshell.calix.command_templates import configuration
from cloudshell.calix.helpers.exceptions import CalixSaveRestoreException

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService

logger = logging.getLogger(__name__)


@define
class SaveRestoreActions:
    _cli_service: CliService

    def save_configuration_to_remote(
        self, folder: str, filename: str, destination_url: str, vrf: str
    ) -> None:
        """Save configuration to remote location."""
        output = CommandTemplateExecutor(
            self._cli_service, configuration.SAVE_CONFIG_REMOTE
        ).execute_command(
            folder=folder, filename=filename, url=destination_url, vrf=vrf or None
        )

        if "error" in output.lower():
            raise CalixSaveRestoreException(f"Error during coping file: {output}")

    def copy_configuration(self, src_file: str, dst_file: str) -> None:
        """Save configuration to remote location."""
        output = CommandTemplateExecutor(
            self._cli_service, configuration.COPY_CONFIG_LOCAL
        ).execute_command(src_file=src_file, dst_file=dst_file)
        if "copy completed" not in output.lower():
            msg = "Saving configuration to local file failed."
            logger.error(f"{msg} {output}")
            raise CalixSaveRestoreException(msg)

    def accept_changes(self) -> None:
        """Accept changes."""
        CommandTemplateExecutor(
            self._cli_service, configuration.ACCEPT_CHANGES
        ).execute_command()

    def reload_device(
        self,
        timeout: int,
        action_map: T_ACTION_MAP = None,
        error_map: T_ERROR_MAP = None,
    ) -> None:
        """Reload device."""
        try:
            CommandTemplateExecutor(
                cli_service=self._cli_service,
                command_template=configuration.RELOAD,
                action_map=action_map,
                error_map=error_map,
            ).execute_command()
            time.sleep(120)
        except SessionException:
            logger.info("Device rebooted, starting reconnect")
        self._cli_service.reconnect(timeout)

    def load_configuration_from_remote(
        self, folder: str, url: str, filename: str, vrf: str
    ) -> None:
        """Load configuration from file."""
        output = CommandTemplateExecutor(
            self._cli_service, configuration.LOAD_CONFIG_REMOTE
        ).execute_command(
            folder=folder,
            url=url,
            filename=filename,
            vrf=vrf or None,
        )

        if "error" in output.lower():
            raise CalixSaveRestoreException(f"Error during coping file: {output}")

    @retry(
        stop_max_delay=5000,
        wait_fixed=2000,
        wait_random_min=2000,
        wait_random_max=5000,
        retry_on_result=lambda result: result is None,
    )
    def check_file_transfer_status(self) -> str:
        output = CommandTemplateExecutor(
            self._cli_service, configuration.CHECK_FILE_STATUS_TAB, remove_prompt=True
        ).execute_command()
        status = configuration.CHECK_FILE_STATUS_RE.sub("", output).strip(" \t\r\n")
        if "success" in status.lower():
            return status
        else:
            error = status.strip(" \t\r\n")
            raise CalixSaveRestoreException(f"Error during coping file: {error}")

    def delete_local_config_file(self, filename: str) -> None:
        """Remove configuration file from local storage."""
        CommandTemplateExecutor(
            self._cli_service, configuration.DELETE_LOCAL_CONFIG
        ).execute_command(filename=filename)
        time.sleep(1)
        check_file_deleted = (
            CommandTemplateExecutor(
                self._cli_service, configuration.CHECK_FILE_DELETED, remove_prompt=True
            )
            .execute_command(filename=filename)
            .strip(" \t\r\n")
        )
        if check_file_deleted:
            logger.warning(
                "Attention, Shell failed to remove temp config from the device. "
                "Please check debug Logs for details."
            )

    def load_configuration_from_local(self, file_path, conf_type, append, store):
        """Load configuration from file."""
        if store and append:
            output = CommandTemplateExecutor(
                self._cli_service,
                configuration.LOAD_CONFIG_LOCAL,  # TODO There is no such configuration template
            ).execute_command(
                file_path=file_path, config=conf_type, append="", store=""
            )
        elif store and not append:
            output = CommandTemplateExecutor(
                self._cli_service, configuration.LOAD_CONFIG_LOCAL  # TODO There is no such configuration template
            ).execute_command(file_path=file_path, config=conf_type, store="")
        else:
            output = CommandTemplateExecutor(
                self._cli_service, configuration.LOAD_CONFIG_LOCAL  # TODO There is no such configuration template
            ).execute_command(file_path=file_path, config=conf_type)

        if "% " in output:
            msg = f"Loading configuration from local file {file_path} failed."
            logger.error(f"{msg} {output}")
            raise CalixSaveRestoreException(msg)
