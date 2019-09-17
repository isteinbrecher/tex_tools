# -*- coding: utf-8 -*-
"""
Replace commands in a latex document.
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
        'Replace the name of a command in a whole tex document (optional also '
        + 'in included files). Per default only the differences are shown.'))
    parser.add_argument('root_tex_path', help=('path to the root of the tex '
            + 'document, where the command should be replaced'))
    parser.add_argument('command_old', help='name of the command to replace')
    parser.add_argument('command_new', help='name of the new command')

    parser.add_argument('-r', '--recursive', action='store_true',
        help='recursively go through included files')
#    parser.add_argument('-v', '--verbose', action='store_true',
#        help='increase output verbosity')
    parser.add_argument('-p', '--perform', action='store_true',
        help='actually replace the commands in the file, default is dry run')

    args = parser.parse_args()

    # Get the full root document path.
    if os.path.isabs(args.root_tex_path):
        full_root_path = args.root_tex_path
    else:
        full_root_path = os.path.join(os.getcwd(), args.root_tex_path)

    # Load the root document.
    root = LaTeXFile(full_root_path, recursive=args.recursive)
    root.replace(args.command_old, args.command_new, dry_run=not args.perform,
        verbose=True)
    if not args.perform:
        print('This was a dry run. To actually replace the command names, set '
            + 'the option -p')
