import os
import sys
import logging
import argparse
import modules as wap # because it was previously called warcraft-addon-packager, or WAP for short

from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logs", f'addonTools{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')

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
    prog = "addontools.py",
    description="A python toolbox for Warcraft addon development",
    epilog="Made by Ghost - https://github.com/Ghostamoose/warcraft-addon-tools"
)
subparsers = parser.add_subparsers(title="subcommands", description="valid subcommands", dest="subcommand", help="subcommand help?")

action_parser = subparsers.add_parser("make", help="Action to build specific parts of your project.")
action_parser.add_argument("action", metavar="action", type=str, help="Specific part of your project to build.")
action_parser.add_argument("-d", "--directory", metavar="directory", dest="directory", type=str, required=True, help=f"Path to the folder that contains your {wap.DOTFILE_NAME} file")

logger.debug(f"Using Python version {sys.version}")

VALID_ACTIONS = ["make"]

def make(make_args):
    if make_args.action == "libs":
        logger.debug("Starting LibFetch...")

        if not os.path.exists(make_args.directory):
            raise FileNotFoundError(f"Directory path does not exist, please enter the path to the folder containing your {wap.DOTFILE_NAME} file.")

        lib_fetcher = wap.LibFetch(make_args.directory)
        fetch = lib_fetcher.get_external_libs()

        if not fetch:
            logger.error("Error occurred while fetching external dependencies.")
            sys.exit(1)

action_parser.set_defaults(func=make)

args = parser.parse_args()
args.func(args)

