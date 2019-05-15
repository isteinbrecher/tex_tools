# -*- coding: utf-8 -*-
"""
Replace commands in a latex document.
"""


# Import python modules.
import re
import os
import argparse
from termcolor import colored


# Global variables.
ROOT_DIRECTORY = ''


def get_includes(line):
    """Check if this line has an include or input command."""
    paths = []
    pattern = r'\\(include|input) *\{.*}'
    for match in re.finditer(pattern, line):
        string = match.string
        file = string.split('{')[1].split('}')[0]
        paths.append(file)
    return paths


def get_commands_in_string(string, command):
    """Return all matches for command in string."""

    pattern = r'\\({})([^a-zA-Z]|$)'.format(command)
    return list(re.finditer(pattern, string))


def split_line_comment(line):
    """Split the line into a code and comment part."""

    # Search for a comment in the middle of the line.
    pattern = r'(^|[^\\])%'
    match = re.search(pattern, line)
    if match:
        split_index = list(match.span())[1] - 1
        return [line[:split_index], line[split_index:]]
    return [line, '']


class LaTeXFile(object):
    """
    This class represents a single tex file.
    """

    def __init__(self, path, *, recursive=False):
        """
        Set up the file, and load the contents to a list.
        """

        # Get the full file path.
        if os.path.isabs(path):
            self.path = path
        else:
            self.path = os.path.join(ROOT_DIRECTORY, path)

        self.lines = [split_line_comment(line.rstrip('\n'))
            for line in open(self.path)]
        self.includes = []

        # Flag if something in the file changed.
        self._changed = False

        if recursive:
            # Get all include paths.
            paths = []
            for line, _comment in self.lines:
                paths.extend(get_includes(line))

            # Create the sub files.
            for path in paths:
                self.includes.append(LaTeXFile(path, recursive=recursive))

    def replace(self, command_name, command_name_new, *, dry_run=True,
            verbose=True):
        """
        Replace a command name in this file and all subfiles.
        """

        if verbose:
            print('{}'.format(os.path.relpath(self.path, ROOT_DIRECTORY)))

        new_lines = []
        for i, [line, comment] in enumerate(self.lines):
            matches = get_commands_in_string(line, command_name)

            # Get a list with the line split up between the replacement parts.
            old_parts = []
            start_index = 0
            for match in reversed(matches):
                span = match.span()
                old_parts.append(line[start_index:span[0]])
                if span[1] - span[0] - len(command_name) == 2:
                    start_index = span[1] - 1
                else:
                    start_index = span[1]
            old_parts.append(line[start_index:])

            if verbose and len(matches) > 0:
                old_string = '\\{}'.format(
                    colored(command_name, 'red')).join(old_parts)
                new_string = '\\{}'.format(
                    colored(command_name_new, 'green')).join(old_parts)
                print('{} {}{}'.format(i + 1, old_string, comment))
                print('{} {}{}'.format(i + 1, new_string, comment))

            # Replace the commands in reverse order.
            if len(matches) > 0:
                self._changed = True
                new_lines.append(
                    ['\\{}'.format(command_name_new).join(old_parts), comment])
            else:
                new_lines.append([line, comment])

        if (not dry_run) and self._changed:
            # Save the replaced file.
            with open(self.path, 'w') as file:
                for line, comment in new_lines:
                    file.write(line)
                    file.write(comment)
                    file.write(os.linesep)

        for subfile in self.includes:
            subfile.replace(command_name, command_name_new, dry_run=dry_run,
                verbose=verbose)


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
    ROOT_DIRECTORY = os.path.dirname(full_root_path)

    # Load the root document.
    root = LaTeXFile(full_root_path, recursive=args.recursive)
    root.replace(args.command_old, args.command_new, dry_run=not args.perform,
        verbose=True)
    if not args.perform:
        print('This was a dry run. To actually replace the command names, set '
            + 'the option -p')
