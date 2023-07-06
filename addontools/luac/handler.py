import addontools


def luac_handler(luacheck_args):
    args = []

    if luacheck_args.action == "globals":
        if luacheck_args.directory:
            args.append(luacheck_args.directory)
        if luacheck_args.luacheck:
            args.append(luacheck_args.luacheck)
        if luacheck_args.luac:
            args.append(luacheck_args.luac)

        luacheck = addontools.luac.LuaCheck(*args)

        luacheck.add_global_variables_to_luacheckrc()

    if luacheck_args.action == "debug":
        luacheck_file = "F:/warcraft-addon-tools/test/.luacheckrc"
        print(addontools.luac.LuaCheckParser(luacheck_file).parse_luacheck_file())
