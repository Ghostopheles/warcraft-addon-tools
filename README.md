# Warcraft Addon Dev Tools
Python CLI tools for World of Warcraft Addon development

## Requirements
- Requires Python 3.8.8 or greater
- Requires [`git`](https://github.com/git-guides/install-git) and `svn` to be installed and properly mapped on your `PATH`
- Requires [`pyyaml`](https://pypi.org/project/PyYAML/)

You can install [`pyyaml`](https://pypi.org/project/PyYAML/) and any other Python package dependencies with `pip install -r requirements.txt`

## Usage
**This will generate a log file beside the .py file!**
### Commands
`make libs`: Grabs external dependencies defined in your .pkgmeta file and places them in the correct folder. For use during development.

### Arguments:
`-d --directory`: Path to the folder containing your addon and the .pkgmeta file.

Example:
```
python addontools.py make libs -d "<your_addon>/.pkgmeta"
```

You can always use `-h` for help as well!

## Final Note

Please do give me suggestions for more tools that could make addon development easier!
