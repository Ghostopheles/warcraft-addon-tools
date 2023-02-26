import logging
import tools

logger = logging.getLogger("addon-tools.addon.handler")


def create_handler(create_args):
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

            if len(author) > 0:
                break
            else:
                logger.error("Please enter an author name.")
                continue
    else:
        author = create_args.author

    # Prompt for addons directory
    if not create_args.directory:
        while True:
            directory = input(
                "Enter the path to your World of Warcraft addons folder: "
            )

            if len(directory) > 0:
                break
            else:
                logger.error("Please enter the path to your addons folder.")
                continue
    else:
        directory = create_args.directory

    # Finally build the addon
    tools.addon.Builder(name, author, directory).create_new_addon()
