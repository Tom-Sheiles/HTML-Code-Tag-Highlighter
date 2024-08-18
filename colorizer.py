#!/bin/python3
#
# Copyright (c) 2024 Tomas Sheiles
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to
# whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
# OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import re
import sys

# Description: Replaces a subset of HTML characters that need to be escaped.
#              Will replace < > \ &
# Parameters:
# input_buffer: string - all intances of the matching characters in this string will be replaced
# 
# Returns: A new string with all matching characters replaced with their HTML code
def html_escape(input_buffer):
    escape_chars = [('<', '&lt;'), ('>', '&gt;'), ('\\', '&#39')]
    out_buffer = input_buffer.replace('&', "&amp;")
    for char, esc in escape_chars:
        out_buffer = out_buffer.replace(char, esc)
    return out_buffer


# Description: Parse a dictionary of colors where the key is the name of each type of token and the value
#              is the HTML color code that token should be colored
# Parameters:
# input_lines: [string] - takes an arry of strings where each element should be the raw string rule for how to map a token name to a color. In the form: [TokenName]: [HTMLColor]
#
# Returns: A dictionary that can be used to lookup what color a token should be colored based on its type
def get_colors(input_lines):
    colors = {}
    for line in input_lines: 
        line = line.replace(" ", "").replace("\n", "")
        lhs, rhs = line.split(":")
        colors[lhs] = rhs
    return colors


# Description: Parse a list of token names and associate them with a regular expression.
#
# Parameters:
# input_lines: [string] - takes an array of strings where each element should be the raw string for a mapping between a token name and regular expression that defines how to identify
#                         that token. In the form [TokenName]: [RegularExpression].
#
# Returns: A list of Token names and the regular expressions that can be used to find that rule. These rules should match the colors in the colors dictionary.
#          A Token can have multiple rules that define it, all of which will resolve to the same output color.
#          The order in the list is the priority by which the patterns will be matched
def get_rules(input_lines):
    rules = []
    for line in input_lines:
        line = line.strip().replace("\n", "")
        lhs, rhs = line.split(":",1)
        rules.append( (lhs, rhs.strip()) )
    return rules


# Description: Color elements of a string according to a list of regular expression rules that defines how to find certain tokens and a list of colors that the rules map to.
#
# Parameters:
# input_buffer: string - The string to color
# colors: {TokenName: Color} - A hashmap of token names and their associated color
# rules: [TokenName: Rule] - a list of token names and the regular expression used to find them
#
# Returns: A string of the colorized HTML output defined by set colors and rules
def colorize_string(input_buffer, colors, rules):
    index = 0
    output_buffer = ""
    while index <= len(input_buffer)-1:
        found = False
        for rule in list(rules):
            match = re.search("^" + rule[1], input_buffer[index:])
            if(match):
                if match.lastindex and match.lastindex > 1:
                    output_buffer += f"<span style=\"color:{colors[rule[0]]}\">{match.group(1)}</span>"
                    index = index + len(match.group(1))
                else:
                    output_buffer += f"<span style=\"color:{colors[rule[0]]}\">{match.group()}</span>"
                    index = index + len(match.group())
                found = True
                break

        if(not found):
            output_buffer += input_buffer[index]
            index = index + 1
    return output_buffer


def print_usage_and_exit():
        print(
'''usage: colorize.py [options]
                 
    file options:
    -f, --file      file to be colorized
    -r, --rules     file containing regular expressions
    -c, --colors    file containing colorscheme

    -h, --help      print this message
''')
        exit()


def parse_command_line(cmd_line):
    file = ""
    rules = ""
    colors = ""

    index = 0
    while index < len(cmd_line):
        if cmd_line[index] == "-f" or cmd_line[index] == "--file":
            file = cmd_line[index+1]
            index = index + 2
        elif cmd_line[index] == "-r" or cmd_line[index] == "--rules":
            rules = cmd_line[index+1]
            index = index + 2
        elif cmd_line[index] == "-c" or cmd_line[index] == "--colors":
            colors = cmd_line[index+1]
            index = index + 2
        elif cmd_line[index] == "-h" or cmd_line[index] == "--help":
            print_usage_and_exit()
        else:
            index = index + 1
    return (file, rules, colors)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage_and_exit()

    file, rules, colors = parse_command_line(sys.argv)
    input_buffer = html_escape(open(file, "r").read())
    output_buffer = colorize_string(input_buffer, get_colors(open(colors, "r").readlines()), get_rules(open(rules, "r").read().strip().split("\n")))
    print("<pre><code>" + output_buffer + "</code></pre>")