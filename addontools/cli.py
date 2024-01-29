import os
import sys
import json
import logging
import logging.config
import argparse
import addontools as wap  # because it was previously called warcraft-addon-packager... or wap

LOG_LEVEL = logging.DEBUG

logger = logging.getLogger("addon-tools")

log_config_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "logging", "log_config.json"
)
with open(log_config_path) as f:
    config = json.load(f)
logging.config.dictConfig(config)

parser = argparse.ArgumentParser(
    prog="wat",
    usage="%(prog)s [options]",
    description="A Python toolbox for World of Warcraft addon development",
    epilog="Made by Ghost - https://github.com/Ghostopheles/warcraft-addon-tools",
)
subparsers = parser.add_subparsers(title="commands", dest="subcommand")

# Build action tools

action_parser = subparsers.add_parser(
    "make", help="Build specific parts of your project."
)
action_parser.add_argument(
    "action", metavar="action", type=str, help="Specific part of your project to build."
)
action_parser.add_argument(
    "-d",
    metavar="directory",
    dest="directory",
    type=str,
    required=False,
    help=f"Path to the folder that contains your {wap.cfg.filenames.PKGMETA_NAME} file. Defaults to current working directory.",
)

action_parser.set_defaults(func=wap.make.make_handler)

# Addon builder tools

create_parser = subparsers.add_parser("create", help="Create a new addon.")
create_parser.add_argument(
    "-d",
    metavar="directory",
    dest="directory",
    required=False,
    type=str,
    help="Path to your WoW addons folder.",
)
create_parser.add_argument(
    "-n",
    metavar="name",
    dest="name",
    required=False,
    type=str,
    help="Name of your new addon.",
)
create_parser.add_argument(
    "-a",
    metavar="author",
    dest="author",
    required=False,
    type=str,
    help="Your name, for use in the .toc file.",
)

create_parser.set_defaults(func=wap.addon.create_handler)

# LuaCheck tools

luacheck_parser = subparsers.add_parser("luacheck", help="Luacheck functions.")
luacheck_parser.add_argument(
    "action",
    metavar="action",
    type=str,
    choices=["globals"],
    help="Luacheck action to execute. Supported: globals",
)
luacheck_parser.add_argument(
    "-d",
    metavar="directory",
    dest="directory",
    required=False,
    type=str,
    help="Path to your addon folder.",
)
luacheck_parser.add_argument(
    "-lc",
    metavar="luacheck file",
    dest="luacheck",
    required=False,
    type=str,
    help=f"Path to your {wap.cfg.filenames.LUACHECK_NAME} file.",
)
luacheck_parser.add_argument(
    "-p",
    metavar="luac path",
    dest="luac",
    required=False,
    type=str,
    help="Path to luac.exe.",
)

luacheck_parser.set_defaults(func=wap.luac.luac_handler)

# wap.start.register_start_parser(subparsers)
wap.agent.register_agent_parser(subparsers)

logger.info(f"Using Python version {sys.version}")

args = parser.parse_args()

if not hasattr(args, "func"):
    logger.error(
        "No command chosen. Please enter a command. For help use -h or --help."
    )
    sys.exit(1)

args.func(args)

sys.exit(0)
