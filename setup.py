from setuptools import setup

setup(
    name="warcraft-addon-tools",
    version="0.1.0",
    packages=["addontools"],
    entry_points={
        "console_scripts": [
            "wat=addontools.cli:main",
        ],
    },
    install_requires=[
        "pyyaml",
    ],
)
