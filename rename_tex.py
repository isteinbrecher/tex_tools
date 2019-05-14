# -*- coding: utf-8 -*-
"""
Replace commands in a latex document.
"""



import re
import os


class LaTeXCommand(object):


    def __init__(self, match, i_line):
        self.i_line = i_line


        print(dir(match))
        print(match)
        print(match.start)
        print(match.span)

        #self.i_char = i_char




def split_relevant_line(line):
    relevant_char = []
    comment_char = []
    prev_char = ''
    is_comment = False
    for i, char in enumerate(line):
        if (is_comment == False and (char == '%' and not prev_char == '\\')):
            # Comment ends this line.
            is_comment = True
        prev_char = char

        if not is_comment:
            relevant_char.append(char)
        else:
            comment_char.append(char)


    return [''.join(relevant_char), ''.join(comment_char)]


def get_relevant_line(line):
    return split_relevant_line(line)[0]



def line_to_include(line):
    line_short = get_relevant_line(line)
    paths = []
    for match in re.finditer(r'\\(include|input) *\{.*}', line_short):
        string = match.string
        file = string.split('{')[1].split('}')[0]
        paths.append(file)
    return paths




def lines_to_include_command(lines):

    includes = []
    for line in lines:
        includes.extend(line_to_include(line))
    return includes



class LaTeXFile(object):

    def __init__(self, path, name):

        # Get lines in the file.
        self.changed = False
        self.path = os.path.join(path, name)
        self.lines = [line for line in open(self.path)]
        includes = lines_to_include_command(self.lines)

        self.includes = []
        for include_path in includes:
            self.includes.append(LaTeXFile(path, include_path))


    def replace(self, command_name, command_name_new):

        self.new_lines = []
        for line in self.lines:

            line_split = split_relevant_line(line)

            # This space will be removed later.
            line_new = line_split[0] + ' '


            search_text = '\\\\({})[^a-zA-Z]'.format(command_name)

            for match in reversed(list(re.finditer(search_text, line_new))):
                span = list(match.span(0))
                line_new = line_new[:span[0]] + '\\' + command_name_new + line_new[span[1]-1:]
                self.changed = True

            line_new = line_new[:-1]

            line_split[0] = line_new

            self.new_lines.append(''.join(line_split))

        if self.changed:
            with open(self.path, 'w') as file:
                file.write(''.join(self.new_lines))

        for subfile in self.includes:
            subfile.replace(command_name, command_name_new)





path = '/home/ivo/unibw/06_Forschung/07_paper/beam-to-solid-paper/tex'
name = 'beam-to-solid-paper.tex'


file = LaTeXFile(path, name)
file.replace('dWs', 'meins')




