import os
import yaml
import logging
import addontools


class YamlParser:
    f"""
    Parses the {addontools.cfg.filenames.PKGMETA_NAME} file used throughout the packager.
    """

    def __init__(self, yaml_file: str):
        self.logger = logging.getLogger("addon-tools.yaml-parser")

        self.dotfile_name = addontools.cfg.filenames.PKGMETA_NAME

        self.yaml_file = yaml_file
        self.__parse_yaml()

    def __parse_yaml(self):
        if not os.path.exists(self.yaml_file):
            raise FileNotFoundError(
                f"{self.dotfile_name} not found in given directory."
            )

        with open(self.yaml_file, "r") as yaml_stream:
            try:
                self.logger.info(f"Parsing {self.dotfile_name} file...")
                self.yaml_data = yaml.safe_load(yaml_stream)

                return True

            except Exception as exc:
                self.logger.error(
                    f"Error occurred when parsing {self.dotfile_name} file."
                )
                self.logger.error(exc)
                return False

    def __getitem__(self, item):
        if item in self.yaml_data:
            return self.yaml_data[item]
        else:
            return None
