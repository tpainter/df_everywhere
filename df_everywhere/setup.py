import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", "zope.interface"], 
                    "excludes": ["tkinter"],
                    "include_files": ['dfeverywhere.conf', 'tilesets\\'],
                    "includes": ["pkg_resources"],
                    "namespace_packages": ["zope"],
                    "silent": True}

# GUI applications require a different base on Windows (the default is for a
# console application). This isn't a gui application, so don't change.
base = None

setup(  name = "df_everywhere",
        version = "0.1",
        description = "df_everywhere",
        options = {"build_exe": build_exe_options},
        executables = [Executable("df_everywhere.py", base=base)])