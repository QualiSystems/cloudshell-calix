import re
import time

from cloudshell.cli.service.command_mode import CommandMode


class EnableCommandMode(CommandMode):
    PROMPT = r"(?:(?!\)).)#\s*$"
    ENTER_COMMAND = ""
    EXIT_COMMAND = ""

    def __init__(self, resource_config):
        """Initialize Enable command mode."""
        self.resource_config = resource_config

        CommandMode.__init__(
            self,
            prompt=EnableCommandMode.PROMPT,
            enter_command=EnableCommandMode.ENTER_COMMAND,
            exit_command=EnableCommandMode.EXIT_COMMAND,
        )

    def enter_action_map(self):
        return {
            "[Pp]assword": lambda session, logger: session.send_line(
                self.resource_config.enable_password, logger
            )
        }


class ConfigCommandMode(CommandMode):
    MAX_ENTER_CONFIG_MODE_RETRIES = 5
    ENTER_CONFIG_RETRY_TIMEOUT = 5
    PROMPT = r"\(config.*\)#\s*$"
    ENTER_COMMAND = "configure"
    EXIT_COMMAND = "end"
    ENTER_ACTION_COMMANDS = []

    def __init__(self, resource_config):
        """Initialize Config command mode."""
        self.resource_config = resource_config

        CommandMode.__init__(
            self,
            prompt=ConfigCommandMode.PROMPT,
            enter_command=ConfigCommandMode.ENTER_COMMAND,
            exit_command=ConfigCommandMode.EXIT_COMMAND,
            enter_action_map=self.enter_action_map(),
        )

    def enter_action_map(self):
        return {fr"{EnableCommandMode.PROMPT}.*$": self._check_config_mode}

    def enter_actions(self, cli_service):
        for cmd in self.ENTER_ACTION_COMMANDS:
            cli_service.send_command(cmd)

    def _check_config_mode(self, session, logger):
        error_message = "Failed to enter config mode, please check logs, for details"
        output = session.hardware_expect(
            "",
            expected_string="{}|{}".format(
                EnableCommandMode.PROMPT, ConfigCommandMode.PROMPT
            ),
            logger=logger,
        )
        retry = 0
        while (
            not re.search(ConfigCommandMode.PROMPT, output)
        ) and retry < self.MAX_ENTER_CONFIG_MODE_RETRIES:
            output = session.hardware_expect(
                ConfigCommandMode.ENTER_COMMAND,
                expected_string="{}|{}".format(
                    EnableCommandMode.PROMPT, ConfigCommandMode.PROMPT
                ),
                logger=logger,
            )
            time.sleep(self.ENTER_CONFIG_RETRY_TIMEOUT)
            retry += 1
        if not re.search(ConfigCommandMode.PROMPT, output):
            raise Exception(error_message)


CommandMode.RELATIONS_DICT = {
    EnableCommandMode: {ConfigCommandMode: {}}
}
