from __future__ import annotations

from cloudshell.cli.command_template.command_template import CommandTemplate

COMMIT = CommandTemplate("commit")
CREATE_FOLDER = CommandTemplate("mkdir {folder_path}")
RELOAD = CommandTemplate("reload [flush-db]")
