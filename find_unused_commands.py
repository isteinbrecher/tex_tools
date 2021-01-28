# -*- coding: utf-8 -*-
"""
Find all defined commands which are never used.
"""


# Import python modules.
import os
import argparse

# Import tex functions.
from tex_tools import LaTeXFile


if __name__ == '__main__':
    # Execution part of script.

    # Define the command line arguments.
    parser = argparse.ArgumentParser(description=(
        'Find unused commands in a LaTeX document.'))
    parser.add_argument('root_tex_path', help=('path to the root of the tex '
            + 'document, where the command should be replaced'))

    args = parser.parse_args()

    # Get the full root document path.
    if os.path.isabs(args.root_tex_path):
        full_root_path = args.root_tex_path
    else:
        full_root_path = os.path.join(os.getcwd(), args.root_tex_path)

    # Load the root document.
    root = LaTeXFile(full_root_path, recursive=True)
    root.check_unused_defined_commands()

