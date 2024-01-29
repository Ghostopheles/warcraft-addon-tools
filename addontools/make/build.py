import os
import sys
import logging

from addontools.make.libFetch import LibFetch

logger = logging.getLogger("addon-tools.make.build")


def make_handler(make_args):
    if make_args.action == "libs":
        _libs(make_args)


def _libs(make_args):
    logger.debug("Starting LibFetch...")
    if not make_args.directory:
        directory = os.getcwd()
    else:
        directory = make_args.directory

    if not os.path.exists(directory):
        raise FileNotFoundError(
            f"Directory path does not exist, please enter the path to the folder containing your .pkgmeta file."
        )

    lib_fetcher = LibFetch(directory)
    fetch = lib_fetcher.get_external_libs()

    if not fetch:
        logger.critical("Error occurred while fetching external dependencies.")
        sys.exit(1)
