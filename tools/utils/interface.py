import os
import shutil
import logging

logger = logging.getLogger("addon-tools.utils.interface")

def verify_interface(interface_name:str | None=None, interfaces:list[str] | None=None):
    if interface_name:
        logger.info(f"Verifying interface {interface_name}...")
        if shutil.which(interface_name):
            logger.info(f"Interface {interface_name} verified.")
            return True
        else:
            logger.error(f"Interface {interface_name} not present.")
            return False
    elif interfaces:
        for alias in interfaces:
            logger.info(f"Verifying interface {interface_name}...")
            if shutil.which(alias):
                logger.info(f"Interface {interface_name} verified.")
                return True, alias
            
            logger.info(f"Interface not found.")
            return False
    else:
        raise ValueError("No arguments provided.")