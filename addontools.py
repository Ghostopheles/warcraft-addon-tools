import os
import sys
import logging
import argparse
import tools as wap  # because it was previously called warcraft-addon-packager, or WAP for short

LOG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), f"addon-tools.log")

LOG_LEVEL = logging.DEBUG

logger = logging.getLogger("addon-tools")
log_format = logging.Formatter("[%(asctime)s]:[%(levelname)s:%(name)s]: %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)

file_handler = logging.FileHandler(filename=LOG_PATH, encoding="utf-8")
file_handler.setFormatter(log_format)

logger.addHandler(file_handler)  # adds filehandler to our logger
logger.addHandler(console_handler)  # adds console handler to our logger

logger.setLevel(LOG_LEVEL)

parser = argparse.ArgumentParser(
    prog="addontools.py",
    description="A Python toolbox for World of Warcraft addon development",
    epilog="Made by Ghost - https://github.com/Ghostamoose/warcraft-addon-tools",
)
subparsers = parser.add_subparsers(
    title="commands", description="tools:", dest="subcommand"
)

# Build action tools

action_parser = subparsers.add_parser(
    "make", help="Build specific parts of your project."
)
action_parser.add_argument(
    "action", metavar="action", type=str, help="Specific part of your project to build."
)
action_parser.add_argument(
    "-d",
    "--directory",
    metavar="directory",
    dest="directory",
    type=str,
    required=True,
    help=f"Path to the folder that contains your {wap.cfg.PKGMETA_NAME} file",
)

action_parser.set_defaults(func=wap.make.build)

# Addon builder tools

create_parser = subparsers.add_parser("create", help="Create a new addon.")
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
create_parser.add_argument(
    "-d",
    metavar="directory",
    dest="directory",
    required=False,
    type=str,
    help="Path to your WoW addons folder.",
)

create_parser.set_defaults(func=wap.addon.create)

# LuaCheck tools

luacheck_parser = subparsers.add_parser("luacheck", help="Luacheck functions.")
luacheck_parser.add_argument(
    "action", metavar="action", type=str, help="Luacheck action to execute."
)
luacheck_parser.add_argument(
    "-lc",
    metavar="luacheck file",
    dest="luacheck",
    required=False,
    type=str,
    help="Path to your .luacheckrc file.",
)
luacheck_parser.add_argument(
    "-p",
    metavar="luac path",
    dest="luac",
    required=False,
    type=str,
    help="Path to 'luac.exe'.",
)
luacheck_parser.add_argument(
    "-d",
    metavar="directory",
    dest="directory",
    required=False,
    type=str,
    help="Path to your addon folder.",
)

luacheck_parser.set_defaults(func=wap.luac.luac)

logger.debug(f"Using Python version {sys.version}")

args = parser.parse_args()

if not hasattr(args, "func"):
    logger.error("No command chosen. Please try again.")
    sys.exit(1)

args.func(args)

sys.exit(0)
