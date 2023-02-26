import re
import tools


class LuaCheckPattern:
    """A class for holding/interacting with LuaCheck patterns."""

    SEPARATOR = "/"
    REGEX_SEPERATOR = "|"

    def __init__(self, pattern: str):
        pattern = pattern.replace('",', "").replace('"', "")
        self.raw = pattern

        patterns = f"({self.raw})".replace(self.SEPARATOR, self.REGEX_SEPERATOR)
        self.regex_patterns = re.compile(patterns)


class LuaCheckParser:
    SOF = "{"
    EOF = "};"

    def __init__(self, luacheck_file: str):
        self.luacheck_file = luacheck_file

    def sanitize_line(self, line: str):
        line = line.replace("\t", "")
        line = line.replace("\n", "")
        line = line.replace('",', "").replace('"', "")
        return line

    def parse_variable(self, line: str):
        entry = line.replace(" ", "").split("=")

        variable_name = entry.pop(0)
        variable_value = str(*entry)

        return variable_name, variable_value

    def parse_luacheck_file(self):
        with open(self.luacheck_file, "r") as luacheck:
            luacheck_data = {field: [] for field in tools.cfg.LC_FIELDS_TO_READ}
            lines = luacheck.readlines()

            in_field = False
            current_field = ""

            for line in lines:
                line = self.sanitize_line(line)

                if line.startswith("--"):
                    continue

                if line.startswith(self.EOF) and in_field:
                    in_field = False
                    current_field = ""
                    continue

                if line and in_field:
                    if current_field not in luacheck_data:
                        continue
                    else:
                        luacheck_data[current_field].append(line.replace("\\\\", "/"))
                    continue

                elif line and line.split(" ")[-1] != (self.SOF[-1] or self.EOF):
                    variable_name, variable_value = self.parse_variable(line)

                    if "meta" not in luacheck_data:
                        luacheck_data["meta"] = []

                    luacheck_data["meta"].append(
                        [variable_name, variable_value.replace(";", "")]
                    )

                if line.split(" ")[-1] == self.SOF and not in_field:
                    in_field = True
                    current_field = line.split(" ")[0]
                    continue

        luacheck_data["ignore"] = [
            LuaCheckPattern(pattern) for pattern in luacheck_data["ignore"]
        ]

        return luacheck_data
