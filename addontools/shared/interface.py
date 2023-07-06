import os
import shutil
import logging

logger = logging.getLogger("addon-tools.utils.interface")


def verify_interface(interface: str | list[str]):
    if isinstance(interface, str):
        logger.info(f"Verifying single interface {interface}...")
        if shutil.which(interface):
            logger.debug(f"Interface {interface} verified.")
            return interface
        else:
            logger.error(f"Interface {interface} not present.")
            return False
    elif isinstance(interface, list):
        for alias in interface:
            logger.debug(f"Verifying interface: '{alias}'")
            if shutil.which(alias):
                logger.debug(f"Interface `{alias}` verified.")
                return alias

        logger.debug(f"Interface not found.")
        return False
    else:
        raise ValueError("Unable to verify interface. No arguments provided.")
