import os
import logging

class AddonBuilder:
    f"""
        Class for creating new addons from scratch.
    """
    def __init__(self, name:str, author:str, directory:str):
        assert os.path.exists(directory)

        self.name = name
        self.author = author
        self.directory = directory
        self.logger = logging.getLogger("addon-tools.addon-builder")

    def create_new_addon(self):
        # First we make the folder for the addon
        self.logger.info("Creating Addon directory...")
        addon_path = os.path.join(self.directory, self.name)
        if os.path.exists(addon_path):
            raise FileExistsError("Addon folder already exists.")
        
        os.mkdir(addon_path)

        # Now we make the .toc file
        self.logger.info("Generating .toc file...")
        toc_contents = [
            f"## Interface: 100000\n",
            f"## Title: {self.name}\n",
            f"## Notes: Notes go here!\n",
            f"## Author: Author name here!\n",
            f"## Version: 0.1\n",
            f"\n",
            f"{self.name}.lua"
        ]

        with open(os.path.join(addon_path, f"{self.name}.toc"), "w") as toc:
            toc.writelines(toc_contents)

        # Then make the base .lua file
        self.logger.info("Generating .lua file...")
        lua_contents = [
            "-------------------------------------------\n",
            "-- Hey! Put some fun information about your addon here!\n",
            "-- Maybe put your name here?\n",
            "-- To-do list maybe?\n",
            "-------------------------------------------\n"
        ]

        with open(os.path.join(addon_path, f"{self.name}.lua"), "w") as lua_file:
            lua_file.writelines(lua_contents)

        self.logger.info("Addon created!")

if __name__ == "__main__":
    pass