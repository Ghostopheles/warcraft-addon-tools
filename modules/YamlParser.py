import os
import yaml
import shutil
import logging
import subprocess

class YamlParser:
    """
        Class for parsing the .pkgmeta file used throughout the packager.
    """
    def __init__(self):
        self.logger = logging.getLogger("pkg-helper.yaml-parser")
        self.dotfile_name = ".pkgmeta"
