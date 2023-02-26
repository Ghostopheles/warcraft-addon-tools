import re
import os
import shutil
import logging
import subprocess

import tools


class LuaCheck:
    f"""
    Class for managing and updating the {tools.cfg.filenames.LUACHECK_NAME} file.
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
        self.logger.info("Finding luac path...")

        luac_path = None

        for alias in tools.cfg.luac.LC_COMMON_ALIASES:
            if shutil.which(alias):
                luac_path = alias

        if not luac_path:
            raise EnvironmentError(
                'luac 5.1 not found. Specify a custom luac path with -p "path/to/luac.exe"'
            )
        else:
            return luac_path

    def luac_version_supported(self):
        self.logger.info("Checking luac version...")

        if not shutil.which("luac") and self.luac_path == "luac":
            self.logger.critical(
                'luac not found on system PATH. Specify a custom luac path with -p "path/to/luac.exe"'
            )
            return False

        luac_out = subprocess.run(
            f"{self.luac_path} -v", capture_output=True, shell=True
        )

        # This is sort of ugly but all it does is take the version string and pick out the numbers.
        luac_version = luac_out.stdout.decode().split(" ")[1].split(".")

        return luac_version in tools.cfg.luac.LC_SUPPORTED_VERSIONS

    def get_luacheck_file(self):
        self.logger.info(f"Searching for {tools.cfg.filenames.LUACHECK_NAME}...")
        luacheck_file = None

        for file in os.listdir(self.directory):
            if file.endswith(tools.cfg.filenames.LUACHECK_NAME):
                luacheck_file = os.path.join(self.directory, file)

        if not luacheck_file:
            raise FileNotFoundError(
                f'{tools.cfg.filenames.LUACHECK_NAME} file not found. Specify a custom path with -lc "path/to/{tools.cfg.filenames.LUACHECK_NAME}"'
            )

        return luacheck_file

    def get_all_lua_files(self):
        lua_files = []

        for root, dirs, files in os.walk(self.directory, topdown=True):
            parent_dir = root.split("\\")[-1]
            for dir in dirs:
                dirpath = os.path.join(parent_dir, dir)
                if dirpath.replace("\\", "/").lower() in (
                    path.lower() for path in self.luacheck_data["exclude_files"]
                ):
                    dirs.remove(dir)
                    continue
            for name in files:
                if name.endswith(".lua"):
                    if any(
                        exclude.split("/")[-1] in name
                        for exclude in self.luacheck_data["exclude_files"]
                    ):
                        continue
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

        parser = tools.luac.LuaCheckParser(self.luacheck_file)
        self.luacheck_data = parser.parse_luacheck_file()

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
                if "GETGLOBAL" in line or "SETGLOBAL" in line:
                    line = line.split(" ")
                    global_variables.append(line[-1])

        return [*set(global_variables)]

    def create_backup_luacheck(self):
        self.logger.info("Backing up luacheck file...")
        backup_filename = self.luacheck_file + ".bak"
        if os.path.exists(backup_filename):
            i = 1
            while os.path.exists(f"{backup_filename}{i}"):
                i += 1
                if i >= 5:
                    self.logger.warning(
                        ".luacheckrc will only keep 5 backups. Clear your backups!"
                    )
                    break
            backup_filename = f"{backup_filename}{i}"

        shutil.copyfile(self.luacheck_file, backup_filename)

    def apply_ignore_patterns(self, ignore_patterns, var: str) -> bool:
        for luac_pattern in ignore_patterns:
            result = luac_pattern.regex_patterns.findall(var)
            if result:
                return True

        return False

    def filter_globals(self, new_globals: list[str]):
        if not new_globals:
            return False

        self.logger.info("Filtering globals...")

        ignore_patterns = self.luacheck_data["ignore"]

        globals_to_add = new_globals.copy()

        for variable in globals_to_add:
            if self.apply_ignore_patterns(ignore_patterns, variable):
                new_globals.remove(variable)

        return new_globals

    def add_global_variables_to_luacheckrc(self):
        new_globals = self.get_global_variables_with_luac()

        if not new_globals:
            return False

        globals_to_add = self.filter_globals(new_globals)

        if not globals_to_add:
            return False

        self.create_backup_luacheck()
        self.logger.info("Rebuilding luacheck file...")

        lines_to_write = []

        for meta_var in self.luacheck_data["meta"]:
            value = meta_var[1]

            if value == "true" or value == "false":
                value = value.replace('"', "")
            else:
                value = f'"{value}"'

            meta_var_line = f"{meta_var[0]} = {value};\n"
            lines_to_write.append(meta_var_line)

        lines_to_write.append("\n")
        lines_to_write.append("exclude_files = {\n")

        for exclude in self.luacheck_data["exclude_files"]:
            exclude_line = f'\t"{exclude}",\n'
            lines_to_write.append(exclude_line)

        lines_to_write.append("};")
        lines_to_write.append("\n")
        lines_to_write.append("\nignore = {\n")

        for ignore_pattern in self.luacheck_data["ignore"]:
            lines_to_write.append(f'\t"{ignore_pattern.raw}",\n')

        lines_to_write.append("};")
        lines_to_write.append("\n")
        lines_to_write.append("\nglobals = {\n")

        for var in globals_to_add:
            lines_to_write.append(f'\t"{var}",\n')

        lines_to_write.append("};\n")

        with open(self.luacheck_file, "w") as file:
            file.writelines(lines_to_write)

        total_variables_added = len(globals_to_add)
        for section in self.luacheck_data:
            total_variables_added += len(section)

        self.logger.info(
            f"Rebuilding complete! Added {total_variables_added} global variables to .luacheckrc file."
        )

        return True
