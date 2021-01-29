# -*- coding: utf-8 -*-
"""
Replace commands in a latex document.
"""


# Import python modules.
import re
import os
from termcolor import colored


def get_includes(line):
    """Check if this line has an include or input command."""
    paths = []
    pattern = r'\\(include|input) *\{.*\}'
    for match in re.finditer(pattern, line):
        string = match.string
        file = string.split('{')[1].split('}')[0]
        paths.append(file)
    return paths


def get_all_commands_in_string(string):
    """Return all matches for command in string."""

    pattern = r'\\[a-zA-Z]*'
    return list(re.finditer(pattern, string))


def get_command_in_string(string, command):
    """Return all matches for command in string."""

    all_commands = get_all_commands_in_string(string)
    return_commands = []
    for match in all_commands:
        span = match.span()
        found_name = string[span[0] + 1:span[1]]
        if found_name == command:
            return_commands.append(match)
    return return_commands


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
        self.path = path
        if not os.path.isabs(self.path):
            raise ValueError('The given path "{}" is not absolute!'.format(
                self.path))

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
                if os.path.isabs(path):
                    abs_path = path
                else:
                    abs_path = os.path.join(os.path.dirname(self.path), path)
                self.includes.append(LaTeXFile(abs_path, recursive=recursive))

    def replace(self, command_name, command_name_new, *, dry_run=True,
            verbose=True):
        """
        Replace a command name in this file and all subfiles.
        """

        if verbose:
            print('{}'.format(self.path))

        new_lines = []
        for i, [line, comment] in enumerate(self.lines):
            matches = get_command_in_string(line, command_name)

            # Get a list with the line split up between the replacement parts.
            old_parts = []
            start_index = 0
            for match in matches:
                span = match.span()
                old_parts.append(line[start_index:span[0]])
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

    def _get_defined_commands(self):
        """
        Return all commands that are defined in this document or an included
        file.
        """

        defined_commands = []
        for i, [line, _comment] in enumerate(self.lines):
            for command_name in ['newcommand', 'renewcommand']:
                matches = get_command_in_string(line, command_name)
                if len(matches) > 1:
                    raise ValueError('Multiple defined commands per line not '
                        'implemented yet')
                elif len(matches) == 1:
                    # Get the text after the command definition.
                    match = matches[0]
                    line_after_command = line[match.span()[1]:]
                    start = line_after_command.find('{')
                    end = line_after_command.find('}')
                    if (start == -1 or end == -1):
                        raise ValueError('Could not find defined command name')
                    defined_commands.append([
                        line_after_command[start + 1:end],
                        self.path,
                        i
                        ])

        for subfile in self.includes:
            defined_commands.extend(subfile._get_defined_commands())

        return defined_commands

    def _get_commands(self):
        """
        Return all commands that are used in this document or an included file.
        """

        used_commands = []
        for _i, [line, _comment] in enumerate(self.lines):
            matches = get_all_commands_in_string(line)
            for match in matches:
                span = match.span()
                used_commands.append(line[span[0]:span[1]])

        for subfile in self.includes:
            used_commands.extend(subfile._get_commands())

        return used_commands

    def check_unused_defined_commands(self):
        """
        Check if there are defined commands in this document which are not
        used.
        """

        defined_commands = {}
        for [command, file, line] in self._get_defined_commands():
            if command in defined_commands.keys():
                raise ValueError(
                    ('Command {} defined twice\n'
                    '{}:{}\n{}:{}').format(
                        command,
                        defined_commands[command][0],
                        defined_commands[command][1],
                        file,
                        line))
            else:
                defined_commands[command] = [file, line, 0]

        used_commands = self._get_commands()
        for command in used_commands:
            if command in defined_commands.keys():
                defined_commands[command][2] += 1

        last_file = ''
        for key, [file, line, count] in defined_commands.items():
            if count == 1:
                if last_file != file:
                    print(colored('{}'.format(file), 'green'))
                    last_file = file
                print('  {}: {} is never used'.format(
                    line,
                    colored(key, 'red')))
