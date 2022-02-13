#!/usr/bin/python

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.calix.command_templates import system


class SystemActions:
    def __init__(self, cli_service, logger):
        """General System actions."""
        self._cli_service = cli_service
        self._logger = logger

    def commit(self):
        """Commit changes."""
        CommandTemplateExecutor(self._cli_service, system.COMMIT).execute_command()

    def create_folder(self, folder_path):
        """Commit changes."""
        CommandTemplateExecutor(
            self._cli_service, system.CREATE_FOLDER
        ).execute_command(folder_path=folder_path)
