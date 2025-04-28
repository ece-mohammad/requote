#!/usr/bin.env python3
# -*- coding: utf-8 -*-
"""
A utility script that unifies string quotes in python files
according to specified style.

Strings in python can be quoted in 3 different ways:
    - single quotes e.g. 'foo'
    - double qoutes e.g. "bar"
    - triple quotes e.g. \"\"\"foo\"\"\" or '''bar'''

Different people prefer different styles, some prefer using
only single quotes or double quotes, while others mix them
together for example quoting single character strings with
single quotes and double quotes for other strings.
As for multi-line strings, some people prefer using
triple quotes while others prefer using line breaks.

while pep8 didn't recommend a specific style for quotes:

    > In Python, single-quoted strings and double-quoted strings
    are the same. This PEP does not make a recommendation for this.
    Pick a rule and stick to it.
    When a string contains single or double quote characters,
    however, use the other one to avoid backslashes in the string.
    It improves readability.

except for triple quoted string:

    > For triple-quoted strings, always use double quote characters
    to be consistent with the docstring convention in PEP 257.

To make the tool as flexible as possible, a style has 2 options:
    1. single character string: single or double quotes.
    2. single line strings: single or double quotes.

Quotes everywhere else (like comments) are not changed,
triple quoted strngs as well, as they should be in double
quotes.

Strings that contain the same quote character, and are quoted
with a different quote character are not changed.

Please, note that it's not recommended to mix single and double
strings usage.But if you like a specific quoting stuyle,
then go for it, this tool is for you. But stick to it, and
be consistent.

"""

import argparse
import enum
import json
import sys
import tokenize
import tomllib
import typing as t
from dataclasses import dataclass
from io import BytesIO
from itertools import takewhile
from pathlib import Path


class ValidationError(Exception):
    ...


class QuoteChar(enum.Enum):
    """An enum type to give names for quoting chars:
    - SINGLE_QUOTE = "'"
    - DOUBLE_QUOTE = '"'
    """

    SINGLE_QUOTE: str = "'"
    DOUBLE_QUOTE: str = '"'


@dataclass()
class QuoteStyle:
    single_char: QuoteChar = QuoteChar.SINGLE_QUOTE
    string: QuoteChar = QuoteChar.DOUBLE_QUOTE

    @staticmethod
    def validate(style: t.Dict[str, str]) -> None:
        """Validaters a style dictionary.

        :param style: a quoting style dictionary that contains the
        quote characters for different strings. A style if valid iff it
        satisfies the following conditions:
            1. contains the keys: single_char and string.
            2. the values for both of them are either
            a single quote or a double quote character.
        example:
            validate_quoting_style(
                {
                    "single_char": "'",
                    "string": "'",
                }
            )
            >>> True

            validate_quoting_style(
                {
                    "single_char": QuoteChar."'",
                }
            )
            >>> False

            validate_quoting_style(
                {
                    "string": QuoteChar."'",
                }
            )
            >>> False

            validate_quoting_style(
                {
                    "single_char": "(",
                    "string": "'",
                }
            )
            >>> False
        :type style: Dict[str, str]
        :raises ValidationError: if the style dictionary doesn't satisfy the
        forementioned criteria
        """
        # validate keys
        if "single_char" not in style.keys() or "string" not in style.keys():
            raise ValidationError(
                f"style doesn't have all keys required for a quoting style:"
                f"{style}")

        # validate quote chars values
        single_char = style["single_char"]
        string = style["string"]
        quote_chars = [q for q in QuoteChar]
        if single_char not in quote_chars or string not in quote_chars:
            raise ValidationError(
                f"style has invalid values for quoting style: {style}")

    @staticmethod
    def from_dict(style: t.Dict[str, str]) -> "QuoteStyle":
        """Create a new QuoteStyle from given style dictionary.

        :param style: a quoting style dictionary that contains the
            quote characters for different strings. Must contain the
            keys: single_char and string. And the values for both of them
            must be either a single quote or a double quote character.
        :type style: Dict[str, str]
        :return: a QuoteStyle object
        :rtype: QuoteStyle
        :raises KeyError: if any of the keys are missing
        :raises ValueError: for invalid quote characters
        """
        return QuoteStyle(
            single_char=QuoteChar(style["single_char"]),
            string=QuoteChar(style["string"]),
        )

    def to_dict(self) -> t.Dict[str, str]:
        """Convert quote style object into a dictionary"""
        return {
            "single_char": self.single_char.value,
            "string": self.string.value
        }

    def __str__(self):
        return f"single_char: {self.single_char}, string: {self.string}"


# default styles
Styles: t.Final[t.Dict[str, QuoteStyle]] = {
    "black":
    QuoteStyle(single_char=QuoteChar.DOUBLE_QUOTE,
               string=QuoteChar.DOUBLE_QUOTE),
    "c_style":
    QuoteStyle(single_char=QuoteChar.SINGLE_QUOTE,
               string=QuoteChar.DOUBLE_QUOTE),
}


def get_parser() -> argparse.ArgumentParser:
    """initialize ArgumentParser instance"""
    parser = argparse.ArgumentParser(description="Requote")
    # input
    parser.add_argument(
        "files",
        help="""Input pythopn files to requote, can be a single file,
        or multiple files. Default: reads from stdin""",
        type=str,
        nargs='*',
        default=['-'],
    )
    # output
    out = parser.add_mutually_exclusive_group()
    out.add_argument(
        "-i",
        "--inplace",
        help="modify files in place.",
        action="store_true",
        default=False,
    )
    # inplace
    out.add_argument(
        "-o",
        "--output",
        help="file to write the output. Default: write to stdout",
        type=str,
        default='-',
    )
    # style
    style = parser.add_mutually_exclusive_group()
    style.add_argument(
        "-s",
        "--style",
        choices=tuple(Styles.keys()),
        default="black",
        help="quoting style to use. Default: black",
    )
    style.add_argument(
        "-c",
        "--conf",
        type=str,
        help="""path to a {json,toml} configuration file
        that contains custom style settings""",
    )
    return parser


def split_quotes(string: str) -> t.Tuple[str, str, str]:
    """remove surrounding chars from a string"""
    stripped = string.strip()
    leader = stripped[0]
    supported_quotes = tuple(i.value for i in QuoteChar)

    if leader not in supported_quotes:
        return ('', string, '')

    quotes = ''.join(list(takewhile(lambda x: x == leader, string)))

    n_quotes = len(quotes)
    return quotes, string[n_quotes:-n_quotes], quotes


def quote_string(string: str, quote_char: QuoteChar, count: int = 1) -> str:
    """quote a given string using quote characters"""
    quotes: str = quote_char.value * count
    return f"{quotes}{string}{quotes}"


def requote_code(code: str, style: QuoteStyle) -> str:
    """Requote strings in a string of python code usign a given style.

    :param code: python code as a string.
    :type code: str
    :param syle: quoting style as a dictionary with keys single_char and string
    :type style: Dict[str, str]
    :return: content of the file requoted using given style.
    :rtype: str
    :raises:
    """
    with BytesIO(code.encode("utf-8")) as f:
        tokens = tokenize.tokenize(f.readline)
        res = []
        for tok in tokens:
            tok_num, tok_val, *_ = tok
            if tok_num == tokenize.STRING:
                l_quote, string, r_quote = split_quotes(tok_val)

                if len(l_quote) == 3:
                    requoted = quote_string(string, QuoteChar.DOUBLE_QUOTE, 3)

                elif len(l_quote) == 2:
                    requoted = quote_string('', style.single_char, 1)

                elif (len(l_quote) == 1 and len(string) < 2
                      and style.single_char.value not in string):
                    requoted = quote_string(string, style.single_char, 1)

                elif (len(l_quote) == 1 and len(string) == 2
                      and string[0] == '\\'
                      and style.single_char.value not in string):
                    requoted = quote_string(string, style.single_char, 1)

                elif (len(l_quote) == 1 and len(string)
                      and style.string.value not in string):
                    requoted = quote_string(string, style.string, 1)

                else:
                    requoted = tok_val

                res.append((tok_num, requoted, *_))
            else:
                res.append((tok_num, tok_val, *_))
    return tokenize.untokenize(res).decode("ascii")


def json_loader(json_str: str) -> t.Dict[str, str]:
    return json.loads(json_str)


def toml_loader(toml_str: str) -> t.Dict[str, str]:
    return tomllib.loads(toml_str)


def load_conf(conf_file: str) -> QuoteStyle:
    """Load quoting style from given conf file"""
    loaders = {".json": json_loader, "toml": toml_loader}

    style_file: Path = Path(conf_file)

    with open(style_file, 'r') as f:
        conf: str = f.read()

    style_dict = loaders[style_file.suffix](conf)
    style = QuoteStyle(style_dict)
    return style


def get_style(name: str, conf_file: str) -> QuoteStyle:
    """Get qpote style by name or from from conf file.
    Named styles takes precedence over conf_files, when both are
    passed to the function.
    """
    if name:
        return Styles[name]

    try:
        style: QuoteStyle = load_conf(conf_file)

    except (ValidationError, KeyError):
        print(f"Invalid style in given conf file: {conf_file}",
              file=sys.stderr)
        sys.exit(1)

    except Exception:
        print(f"Invalid style file: {conf_file}", file=sys.stderr)
        sys.exit(1)

    return style


def read_stdin() -> str:
    """Read code from stdin"""
    code = ''
    while line := sys.stdin.readline():
        code += line
    return code


def main():
    parser = get_parser()
    args = parser.parse_args()
    out = args.output
    results = {}

    # get style (builtin, custom)
    style: QuoteStyle = get_style(args.style, args.conf)

    # stdin
    if '-' in args.files:
        code: str = read_stdin()
        content: str = requote_code(code, style)

        out: str = '-' if args.inplace else out
        results[out] = content

        args.files.clear()

    # files
    for f in args.files:
        src_file: Path = Path(f)
        if not src_file.exists() or not src_file.is_file():
            print(
                f"given path doesn't exist or is not a file: {src_file}",
                file=sys.stderr,
            )
            sys.exit(1)

        if src_file.suffix != ".py":
            print(f"given file is not a python file: {src_file}",
                  file=sys.stderr)
            sys.exit(1)

        with open(src_file) as src:
            code = src.read()

        content = requote_code(code, style)

        if args.inplace:
            results[f] = content

        else:
            results[out] = results.get(out, '') + '\n' + content

    # write results
    for f, res in results.items():
        if f == '-':
            outfile = sys.stdout
        else:
            outfile = open(f, 'w')

        outfile.write(res)

        if f != '-':
            outfile.close()


if __name__ == "__main__":
    main()
