from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

from cloudshell.calix.command_templates import system

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService


@define
class SystemActions:
    _cli_service: CliService

    def commit(self) -> None:
        """Commit changes."""
        CommandTemplateExecutor(self._cli_service, system.COMMIT).execute_command()

    def create_folder(self, folder_path: str) -> None:
        """Commit changes."""
        CommandTemplateExecutor(
            self._cli_service, system.CREATE_FOLDER
        ).execute_command(folder_path=folder_path)
