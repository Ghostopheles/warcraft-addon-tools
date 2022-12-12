import os
import sys
import logging
import argparse
import modules as wap # because it was previously called warcraft-addon-packager, or WAP for short

LOG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), f'addon-tools.log')

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
    description="A Python toolbox for World of Warcraft addon development",
    epilog="Made by Ghost - https://github.com/Ghostamoose/warcraft-addon-tools"
)
subparsers = parser.add_subparsers(title="commands", description="tools:", dest="subcommand")

action_parser = subparsers.add_parser("make", help="Build specific parts of your project.")
action_parser.add_argument("action", metavar="action", type=str, help="Specific part of your project to build.")
action_parser.add_argument("-d", "--directory", metavar="directory", dest="directory", type=str, required=True, help=f"Path to the folder that contains your {wap.DOTFILE_NAME} file")

create_parser = subparsers.add_parser("create", help="Create a new addon.")
create_parser.add_argument("-n", metavar="name", dest="name", required=False, type=str, help="Name of your new addon.")
create_parser.add_argument("-a", metavar="author", dest="author", required=False, type=str, help="Your name, for use in the .toc file.")
create_parser.add_argument("-d", metavar="directory", dest="directory", required=False, type=str, help="The path to your WoW addons folder.")

logger.debug(f"Using Python version {sys.version}")

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

def create(create_args):
    # Prompt user to input a name if none was given through the command line
    if not create_args.name:
        while True:
            name = input("Enter a name for your addon: ")

            if len(name) > 0:
                break
            else:
                logger.error("Please enter a name.")
                continue
    else:
        name = create_args.name
    
    # Prompt for author name
    if not create_args.author:
        while True:
            author = input("Enter an author name: ")

            if len(author) > 0: break
            else:
                logger.error("Please enter an author name.")
                continue
    else:
        author = create_args.author
    
    # Prompt for addons directory
    if not create_args.directory:
        while True:
            directory = input("Enter the path to your World of Warcraft addons folder: ")

            if len(directory) > 0: break
            else:
                logger.error("Please enter the path to your addons folder.")
                continue
    else:
        directory = create_args.directory

    # Finally build the addon
    wap.AddonBuilder(name, author, directory).create_new_addon()

create_parser.set_defaults(func=create)

args = parser.parse_args()
args.func(args)

