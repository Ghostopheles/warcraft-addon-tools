import re
import tools


class LuaCheckPattern:
    """A class for holding/interacting with LuaCheck patterns."""

    SEPARATOR = "/"

    def __init__(self, pattern: str):
        patterns = pattern.split(self.SEPARATOR)
        self.regex_patterns = [re.compile(pattern) for pattern in patterns]

        self.max = len(self.regex_patterns) - 1

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n <= self.max:
            result = self.regex_patterns[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration


class LuaCheckParser:
    SOF = " = {"
    EOF = "};"

    def __init__(self, luacheck_file: str):
        self.luacheck_file = luacheck_file

    def parse_luacheck_file(self):
        existing_globals = {}

        with open(self.luacheck_file, "r") as luacheck:
            lines = luacheck.readlines()

            for field in tools.cfg.LC_FIELDS_TO_READ:
                in_field = False
                existing_globals[field] = []
                print(field)
                for line in lines:
                    if line.startswith(self.EOF) and in_field:
                        break

                    if in_field:
                        entry = line.split('"')
                        if len(entry) > 1:
                            if "\t--" in entry[0]:
                                continue

                            existing_globals[field].append(*entry[1::2])

                    if line.startswith(field + self.SOF):
                        in_field = True
                        continue

            existing_globals["ignore"] = [
                LuaCheckPattern(pattern) for pattern in existing_globals["ignore"]
            ]

        return existing_globals


if __name__ == "__main__":
    luacheck_file = "F:/warcraft-addon-tools/test/.luacheckrc"
    print(LuaCheckParser(luacheck_file).parse_luacheck_file().values())
