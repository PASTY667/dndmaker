"""
Configuration du package DNDMaker
"""

from setuptools import setup, find_packages

setup(
    name="dndmaker",
    version="0.1.0",
    description="Application de gestion de campagne Chroniques Oubliées",
    author="",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.6.0",
        "reportlab>=4.0.0",
        "Pillow>=10.0.0",
        "jsonschema>=4.20.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "dndmaker-cli=dndmaker.ui_cli.main:main",
            "dndmaker-qt=dndmaker.ui_qt.main:main",
            "dndmaker=dndmaker.ui_qt.main:main",  # Alias plus court
        ],
    },
)

