import re

from cloudshell.cli.command_template.command_template import CommandTemplate

SAVE_CONFIG_REMOTE = CommandTemplate(
    "upload file {folder} from-file {filename} to-URI {url} [vrf {vrf}]"
)

LOAD_CONFIG_REMOTE = CommandTemplate(
    "download file {folder} from-URI {url} to-file {filename} [vrf {vrf}]"
)
COPY_CONFIG_LOCAL = CommandTemplate("copy config from {src_file} to {dst_file}")

RELOAD = CommandTemplate(
    "reload all",
    action_map={
        r"[\[\(][Yy]/[Nn][\)\]]": lambda session, logger: session.send_line("y", logger)
    },
)

DELETE_LOCAL_CONFIG = CommandTemplate("delete file config filename {filename}")

CHECK_FILE_DELETED = CommandTemplate(
    "show file contents config files " "| include {filename}"
)

CHECK_FILE_STATUS_TAB = CommandTemplate("show file transfer-status | tab")
CHECK_FILE_STATUS_RE = re.compile(
    r"(\d+(/\d*)*\s*(-|idle)*|LOCATION\s+STATUS|(--)+)", re.IGNORECASE
)
