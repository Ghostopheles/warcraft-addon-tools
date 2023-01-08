import os
import sys
import logging

import tools

logger = logging.getLogger("addon-tools.make.build")


def build(make_args):
    if make_args.action == "libs":
        _libs(make_args)


def _libs(make_args):
    logger.debug("Starting LibFetch...")
    if not os.path.exists(make_args.directory):
        raise FileNotFoundError(
            f"Directory path does not exist, please enter the path to the folder containing your {tools.cfg.PKGMETA_NAME} file."
        )

    lib_fetcher = tools.lib.LibFetch(make_args.directory)
    fetch = lib_fetcher.get_external_libs()

    if not fetch:
        logger.error("Error occurred while fetching external dependencies.")
        sys.exit(1)


if __name__ == "__main__":
    pass
