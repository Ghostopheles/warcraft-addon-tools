import re
import os
import shutil
import logging
import subprocess

import tools


class LuaCheck:
    f"""
    Class for managing and updating the {tools.cfg.LUACHECK_NAME} file.
    """

    def __init__(
        self,
        directory: str | None = None,
        luacheck_file: str | None = None,
        luac_path: str | None = None,
    ):
        self.logger = logging.getLogger("addon-tools.luacheck")

        self.directory = directory or os.getcwd()
        self.luacheck_file = luacheck_file or self.get_luacheck_file()
        self.luac_path = luac_path or self.get_luac_path()

    def get_luac_path(self):
        self.logger.debug("Finding luac path...")

        luac_path = None

        for alias in tools.cfg.LC_COMMON_ALIASES:
            if shutil.which(alias):
                luac_path = alias

        if not luac_path:
            raise EnvironmentError(
                'luac 5.1 not found. Specify a custom luac path with -p "path/to/luac.exe"'
            )
        else:
            return luac_path

    def luac_version_supported(self):
        self.logger.debug("Checking luac version...")

        if not shutil.which("luac") and self.luac_path == "luac":
            self.logger.error(
                'luac not found on system PATH. Specify a custom luac path with -p "path/to/luac.exe"'
            )
            return False

        luac_out = subprocess.run(
            f"{self.luac_path} -v", capture_output=True, shell=True
        )

        # This is sort of ugly but all it does is take the version string and pick out the numbers.
        luac_version = luac_out.stdout.decode().split(" ")[1].split(".")

        return luac_version in tools.cfg.LC_SUPPORTED_VERSIONS

    def get_luacheck_file(self):
        self.logger.info(f"Searching for {tools.cfg.LUACHECK_NAME}...")
        luacheck_file = None

        for file in os.listdir(self.directory):
            if file.endswith(tools.cfg.LUACHECK_NAME):
                luacheck_file = os.path.join(self.directory, file)

        if not luacheck_file:
            raise FileNotFoundError(
                f'{tools.cfg.LUACHECK_NAME} file not found. Specify a custom path with -lc "path/to/{tools.cfg.LUACHECK_NAME}"'
            )

        return luacheck_file

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

    def get_global_variables_with_luac(self) -> list[str] | None:
        if not self.luac_version_supported():
            self.logger.error(
                "Current luac version is not supported. Please use luac version 5.1."
            )
            return

        self.logger.info(
            "Running luac... (this may take a bit depending on your project)"
        )

        lua_files = self.get_all_lua_files()
        global_variables = []

        for file in lua_files:
            try:
                out = subprocess.run(
                    f"luac -l -p {file}", capture_output=True, shell=True
                )
                out_lines = out.stdout.splitlines()
            except Exception as exc:
                self.logger.error(f"Error occurred while running luac on '{file}'.")
                self.logger.error(exc)
                return

            for line in out_lines:
                line = line.decode()
                if "GETGLOBAL" in line:
                    line = line.split(" ")
                    global_variables.append(line[-1])

        # DEBUG REMOVE THIS PLEASE
        global_variables.append("WAP_TEST")
        global_variables.append("TRP3_WAP")

        return [*set(global_variables)]

    def apply_ignore_patterns(self, ignore_patterns, var: str) -> bool:
        for luac_pattern in ignore_patterns:
            for pattern in luac_pattern:
                result = re.search(pattern, var)

                if result:
                    return True

        return False

    def filter_globals(self, new_globals: list[str]):
        if not new_globals:
            return False

        self.logger.debug("Filtering globals...")

        parser = tools.luac.LuaCheckParser(self.luacheck_file)

        existing_globals = parser.parse_luacheck_file()
        ignore_patterns = existing_globals["ignore"].copy()

        del existing_globals["ignore"]

        existing = []
        for ls in existing_globals.values():
            if ls:
                existing.extend(ls)

        globals_to_add = new_globals.copy()

        for variable in globals_to_add:
            if self.apply_ignore_patterns(ignore_patterns, variable):
                new_globals.remove(variable)
            elif variable in existing:
                new_globals.remove(variable)

        return new_globals

    def add_global_variables_to_luacheckrc(self):
        globals_to_add = self.get_global_variables_with_luac()

        if not globals_to_add:
            return False

        globals_to_add = self.filter_globals(globals_to_add)

        self.logger.info("Found new globals.")
        print(globals_to_add)