from __future__ import annotations

import logging
import re
from collections.abc import Collection
from typing import TYPE_CHECKING, ClassVar

from attrs import define, field
from typing_extensions import Self

from cloudshell.cli.configurator import AbstractModeConfigurator
from cloudshell.cli.factory.session_factory import (
    CloudInfoAccessKeySessionFactory,
    ConsoleSessionFactory,
    GenericSessionFactory,
    SessionFactory,
)
from cloudshell.cli.service.cli_service_impl import CliServiceImpl
from cloudshell.cli.service.command_mode_helper import CommandModeHelper
from cloudshell.cli.session.console_ssh import ConsoleSSHSession
from cloudshell.cli.session.console_telnet import ConsoleTelnetSession
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession

from cloudshell.calix.cli.calix_command_modes import (
    ConfigCommandMode,
    EnableCommandMode,
)

if TYPE_CHECKING:
    from cloudshell.cli.service.cli import CLI
    from cloudshell.cli.types import T_COMMAND_MODE_RELATIONS, CliConfigProtocol


@define
class CalixCliConfigurator(AbstractModeConfigurator):
    REGISTERED_SESSIONS: ClassVar[tuple[SessionFactory]] = (
        CloudInfoAccessKeySessionFactory(SSHSession),
        GenericSessionFactory(TelnetSession),
        ConsoleSessionFactory(ConsoleSSHSession),
        ConsoleSessionFactory(
            ConsoleTelnetSession, session_kwargs={"start_with_new_line": False}
        ),
        ConsoleSessionFactory(
            ConsoleTelnetSession, session_kwargs={"start_with_new_line": True}
        ),
    )
    modes: T_COMMAND_MODE_RELATIONS = field(init=False)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.modes = CommandModeHelper.create_command_mode(self._auth)

    @classmethod
    def from_config(
        cls,
        conf: CliConfigProtocol,
        logger: logging.Logger | None = None,
        cli: CLI | None = None,
        registered_sessions: Collection[SessionFactory] | None = None,
    ) -> Self:
        if not logger:
            logger = logging.getLogger(__name__)
        return super().from_config(conf, logger, cli, registered_sessions)

    @property
    def enable_mode(self):
        return self.modes[EnableCommandMode]

    @property
    def config_mode(self):
        return self.modes[ConfigCommandMode]

    def _on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs."""
        cli_service = CliServiceImpl(
            session=session, requested_command_mode=self.enable_mode, logger=logger
        )
        output = cli_service.send_command(
            "terminal screen-length 0", EnableCommandMode.PROMPT
        )
        if re.search(r"syntax\s+error\S*\s+expecting", output, re.IGNORECASE):
            cli_service.reconnect(10)
            cli_service.send_command(
                "terminal screen-length 0", EnableCommandMode.PROMPT
            )
