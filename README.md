# Warcraft Addon Dev Tools
Cross-platform Python CLI tools for World of Warcraft Addon development

## Requirements
- Requires Python 3.8.8 or greater
- Requires [`git`](https://github.com/git-guides/install-git) and `svn` to be installed and properly mapped on your `PATH`
- Requires [`pyyaml`](https://pypi.org/project/PyYAML/)

You can install [`pyyaml`](https://pypi.org/project/PyYAML/) and any other Python package dependencies with `pip install -r requirements.txt`

## Usage
**This will generate a log file beside the .py file!**
### Commands
`make libs`: Grabs external dependencies defined in your .pkgmeta file and places them in the correct folder. For use during development.
- `-d --directory`: Path to the folder containing your addon and the .pkgmeta file.

`create`: Used to generate a basic addon in your World of Warcraft addons folder (or any folder). Saves you a good 45 seconds of creating a new .lua and .toc file! Can be called with no arguments, will prompt the user for the values.
- `-n`: A name for your addon.
- `-a`: An author name.
- `-d`: Path to the folder you want to generate the addon in.

Example:
```
python addontools.py make libs -d "<path>/<to>/<your_addon>"
```

You can always use `-h` for help!

## Final Note

Please do give me suggestions for more tools that could make addon development easier!
