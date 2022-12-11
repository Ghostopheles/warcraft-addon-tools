# Warcraft Addon Dev Tools
Python CLI tools for World of Warcraft Addon development

## Requirements
- Requires Python 3.8.8 or greater
- Requires [`git`](https://github.com/git-guides/install-git) and [`svn`](https://tortoisesvn.net/downloads.html) to be installed and properly mapped on your `PATH`
- Requires [`pyyaml`](https://pypi.org/project/PyYAML/)

## Usage
### Commands
`make libs`: Currently the only tool, grabs external dependencies defined in your .pkgmeta file and places them in the correct folder. For use during development.

Example:
```
python addontools.py make libs -d "<your_addon>/.pkgmeta"
```

You can always use `-h` for help as well!
