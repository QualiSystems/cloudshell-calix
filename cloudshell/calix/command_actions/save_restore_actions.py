import time
from retry import retry

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.calix.command_templates import configuration
from cloudshell.calix.helpers.exceptions import (
    CalixSaveRestoreException,
)
from cloudshell.cli.session.session_exceptions import SessionException


class SaveRestoreActions:
    def __init__(self, cli_service, logger):
        """Save and Restore actions."""
        self._cli_service = cli_service
        self._logger = logger

    def save_configuration_to_remote(self, folder, filename, destination_url, vrf):
        """Save configuration to remote location."""
        output = CommandTemplateExecutor(
            self._cli_service, configuration.SAVE_CONFIG_REMOTE
        ).execute_command(
            folder=folder, filename=filename, url=destination_url, vrf=vrf
        )

        if "error" in output.lower():
            raise CalixSaveRestoreException(f"Error during coping file: {output}")

    def copy_configuration(self, src_file, dst_file):
        """Save configuration to remote location."""
        output = CommandTemplateExecutor(
            self._cli_service, configuration.COPY_CONFIG_LOCAL
        ).execute_command(src_file=src_file, dst_file=dst_file)
        if "copy completed" not in output.lower():
            msg = "Saving configuration to local file failed."
            self._logger.error(f"{msg} {output}")
            raise CalixSaveRestoreException(msg)

    def reload_device(self, timeout, action_map=None, error_map=None):
        """Reload device.

        :param timeout: session reconnect timeout
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        try:
            CommandTemplateExecutor(
                    self._cli_service,
                    configuration.RELOAD,
                    action_map=action_map,
                    error_map=error_map,
                ).execute_command()
            time.sleep(120)
        except SessionException:
            self._logger.info("Device rebooted, starting reconnect")
        self._cli_service.reconnect(timeout)

    def load_configuration_from_remote(
            self, folder, url, filename, vrf
    ):
        """Load configuration from file."""
        output = CommandTemplateExecutor(
            self._cli_service, configuration.LOAD_CONFIG_REMOTE
        ).execute_command(
            folder=folder,
            url=url,
            filename=filename,
            vrf=vrf,
        )

        if "error" in output.lower():
            raise CalixSaveRestoreException(f"Error during coping file: {output}")

    @retry(tries=5, delay=1, backoff=2, max_delay=4)
    def check_file_transfer_status(self):
        output = CommandTemplateExecutor(
            self._cli_service, configuration.CHECK_FILE_STATUS_TAB, remove_prompt=True
        ).execute_command()
        status = configuration.CHECK_FILE_STATUS_RE.sub("", output).strip(" \t\r\n")
        if "success" in status.lower():
            return status
        else:
            error = status.strip(" \t\r\n")
            raise CalixSaveRestoreException(f"Error during coping file: {error}")

    def delete_local_config_file(self, filename):
        CommandTemplateExecutor(
            self._cli_service, configuration.DELETE_LOCAL_CONFIG
        ).execute_command(filename=filename)
        time.sleep(1)
        check_file_deleted = CommandTemplateExecutor(
            self._cli_service, configuration.CHECK_FILE_DELETED, remove_prompt=True
        ).execute_command(filename=filename).strip(" \t\r\n")
        if check_file_deleted:
            self._logger.warnning("Attention, Shell failed to remove temp config from the device. "
                                  "Please check debug Logs for details.")

    def load_configuration_from_local(self, file_path, conf_type, append, store):
        """Load configuration from file."""
        if store and append:
            output = CommandTemplateExecutor(
                self._cli_service, configuration.LOAD_CONFIG_LOCAL
            ).execute_command(
                file_path=file_path, config=conf_type, append="", store=""
            )
        elif store and not append:
            output = CommandTemplateExecutor(
                self._cli_service, configuration.LOAD_CONFIG_LOCAL
            ).execute_command(file_path=file_path, config=conf_type, store="")
        else:
            output = CommandTemplateExecutor(
                self._cli_service, configuration.LOAD_CONFIG_LOCAL
            ).execute_command(file_path=file_path, config=conf_type)

        if "% " in output:
            msg = f"Loading configuration from local file {file_path} failed."
            self._logger.error(f"{msg} {output}")
            raise CalixSaveRestoreException(msg)
