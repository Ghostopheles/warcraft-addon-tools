import re
import os
import shutil
import logging
import subprocess

from modules import LUACHECK_NAME, LC_SUPPORTED_VERSIONS, LC_COMMON_ALIASES

class LuaCheck:
    f"""
        Class for managing and updating the {LUACHECK_NAME} file.
    """

    def __init__(self, directory:str=None, luacheck_file:str=None, luac_path:str=None):
        self.logger = logging.getLogger("addon-tools.luacheck")

        self.directory = directory or os.getcwd()
        self.luacheck_file = luacheck_file or self.get_luacheck_file()
        self.luac_path = luac_path or self.get_luac_path()

    def get_luac_path(self):
        self.logger.debug("Finding luac path...")

        luac_path = None

        for alias in LC_COMMON_ALIASES:
            if shutil.which(alias):
                luac_path = alias
        
        if not luac_path:
            raise EnvironmentError("luac 5.1 not found. Specify a custom luac path with -p \"path/to/luac.exe\"")
        else:
            return luac_path
    
    def luac_version_supported(self):
        self.logger.debug("Checking luac version...")

        if not shutil.which("luac") and self.luac_path == "luac":
            self.logger.error("luac not found on system PATH. Specify a custom luac path with -p \"path/to/luac.exe\"")
            return False

        luac_out = subprocess.run(f"{self.luac_path} -v", capture_output=True, shell=True)

        # This is sort of ugly but all it does is take the version string and pick out the numbers.
        luac_version = luac_out.stdout.decode().split(" ")[1].split(".")

        return luac_version in LC_SUPPORTED_VERSIONS

    def get_luacheck_file(self):
        self.logger.info(f"Searching for {LUACHECK_NAME}...")
        luacheck_file = None

        for file in os.listdir(self.directory):
            if file.endswith(LUACHECK_NAME):
                luacheck_file = os.path.join(self.directory, file)
        
        if not luacheck_file:
            raise FileNotFoundError(f"{LUACHECK_NAME} file not found. Specify a custom path with -lc \"path/to/{LUACHECK_NAME}\"")
        
        return luacheck_file

    def parse_luacheck_file(self):
        with open(self.luacheck_file, "r") as luacheck:
            lines = luacheck.readlines()

            existing_globals = []
            existing_read_globals = []

            in_globals = False
            in_read_globals = False

            # get globals table line numbers, this might be terrible but it works :)
            for line in lines:
                if line.startswith("};") and in_globals:
                    in_globals = False
                    continue

                if in_globals:
                    entry = line.split('"')
                    if len(entry) > 1:
                        existing_globals.append(*entry[1::2])

                if line.startswith("globals = {"):
                    in_globals = True
                    continue

            pattern = "11./^TRP3_"

            m = re.search()

        
        print(existing_globals)


    def get_all_lua_files(self):
        lua_files = []

        for root, dirs, files in os.walk(self.directory):
            for name in files:
                if name.endswith(".lua"):
                    lua_files.append(os.path.abspath(os.path.join(root, name)))
        
        if len(lua_files) > 0:
            return lua_files
        else:
            self.logger.error("No lua files found!")
            raise FileNotFoundError("No lua files found.")

    def get_global_variables_with_luac(self):
        if not self.luac_version_supported():
            self.logger.error("Current luac version is not supported. Please use luac version 5.1.")
            return False

        self.logger.info("Running luac... (this may take a bit depending on your project)")

        lua_files = self.get_all_lua_files()
        global_variables = []
        
        for file in lua_files:
            try:
                out = subprocess.run(f'luac -l -p {file}', capture_output=True, shell=True)
                out_lines = out.stdout.splitlines()
            except Exception as exc:
                self.logger.error(f"Error occurred while running luac on '{file}'.")
                self.logger.error(exc)
                return False
           
            for line in out_lines:
                line = line.decode()
                if "GETGLOBAL" in line:
                    line = line.split(" ")
                    global_variables.append(line[-1])
            
        return [*set(global_variables)]

    def add_global_variables_to_luacheckrc(self):
        self.logger.debug(self.get_global_variables_with_luac())


if __name__ == "__main__":
    test_path = "f:/warcraft-addon-tools/test"
    trp_path = "F:\Total-RP-3"

    luac = LuaCheck(directory="F:\Total-RP-3")
    f = luac.add_global_variables_to_luacheckrc()