#!/usr/bin.env python3
# -*- coding: utf-8 -*-
"""

A utility script that unifies string quotes in python files
according to specified style.

Strings in python can be quoted in 3 different ways:
    - single quotes e.g. 'foo'
    - double quotes e.g. "bar"
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

Quotes everywhere else (like comments) are not changed, and
strings that contain the same quote character.

Please, note that it's not recommended to mix single and double
strings usage. But if you like a specific quoting style,
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

    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'


@dataclass()
class QuoteStyle:
    single_char: QuoteChar = QuoteChar.SINGLE_QUOTE
    string: QuoteChar = QuoteChar.DOUBLE_QUOTE

    def __post_init__(self) -> None:
        self.validate(self.to_dict())

    @staticmethod
    def validate(style: t.Dict[str, str]) -> None:
        """Validates a style dictionary.

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
        validation criteria
        """
        # validate keys
        if "single_char" not in style.keys():
            raise ValidationError(f"Missing 'single_char' key from style: "
                                  f"{style}")

        if "string" not in style.keys():
            raise ValidationError(f"Missing 'string' key from style: "
                                  f"{style}")

        # validate quote chars values
        quote_enums = {q for q in QuoteChar}
        quote_chars = {q.value for q in QuoteChar}
        single_char = style["single_char"]
        string = style["string"]

        if (isinstance(single_char, str) and single_char
                not in quote_chars) or (isinstance(single_char, QuoteChar)
                                        and single_char not in quote_enums):
            raise ValidationError(
                f"style has invalid value for single_char quotes: {style}")

        if (isinstance(string, str) and string not in quote_chars) or (
                isinstance(string, QuoteChar) and string not in quote_enums):
            raise ValidationError(
                f"style has invalid values for string quotes: {style}")

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
            "string": self.string.value,
        }

    def __str__(self) -> str:
        return f"single_char: {self.single_char}, string: {self.string}"


# default styles
Styles: t.Final[t.Dict[str, QuoteStyle]] = {
    "black":
    QuoteStyle(
        single_char=QuoteChar.DOUBLE_QUOTE,
        string=QuoteChar.DOUBLE_QUOTE,
    ),
    "c_style":
    QuoteStyle(
        single_char=QuoteChar.SINGLE_QUOTE,
        string=QuoteChar.DOUBLE_QUOTE,
    ),
}


def get_parser() -> argparse.ArgumentParser:
    """initialize ArgumentParser instance"""
    parser = argparse.ArgumentParser(description="Requote")
    # input
    parser.add_argument(
        "files",
        help="""Input python files to requote, can be a single file,
                or multiple files, or from stdin (using '-'). Can't read
                from both stdin and files at the same time.
                Default: reads from stdin""",
        type=str,
        nargs='*',
        default=['-'],
    )
    # output
    out = parser.add_mutually_exclusive_group()
    out.add_argument(
        "-i",
        "--inplace",
        help="""modify files in place.
                Can't be used with -o OUTPUT.
                Default: False""",
        action="store_true",
        default=False,
    )
    # inplace
    out.add_argument(
        "-o",
        "--output",
        help="""file to write the output, use '-' to write to stdout.
                Can't be used with -i.
                Default: write to stdout""",
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
        help="""quoting style to use.
                Can't be used with -c CONF.
                Default: black""",
    )
    style.add_argument(
        "-c",
        "--conf",
        type=str,
        help="""path to a {json,toml} configuration file
                that contains custom style settings
                Can't be used with -s STYLE.
                Default: None""",
        default=None,
    )
    return parser


def split_quotes(string: str) -> t.Tuple[str, str, str]:
    """remove surrounding chars from a string"""
    stripped = string.strip()
    # get first char, if string is quoted, to handle cases where the string
    # is all quotes like '"', "'"
    leader = stripped[0]
    supported_quotes = {i.value for i in QuoteChar}

    if leader not in supported_quotes:
        return ('', string, '')

    n_quotes = len(list(takewhile(lambda x: x == leader, string)))
    quotes = leader * n_quotes
    return quotes, string[n_quotes:-n_quotes], quotes


def quote_string(string: str, quote_char: QuoteChar, count: int = 1) -> str:
    """quote a given string using quote characters"""
    quotes: str = quote_char.value * count
    return f"{quotes}{string}{quotes}"


def requote_code(code: str, style: QuoteStyle) -> str:
    """Requote strings in a string of python code using a given style.

    :param code: python code as a string.
    :type code: str
    :param style: quoting style as a dictionary with keys single_char and
    string
    :type style: Dict[str, str]
    :return: content of the file requoted using given style.
    :rtype: str
    :raises:
    """

    def requote_string_token(tok_val: str, style: QuoteStyle) -> str:
        """Requote a string token using a given style

        :param tok_val: string to requote
        :type tok_val: str
        :param style: quoting style
        :type style: QuoteStyle
        :return: requoted string if possible, otherwise return original string
        :rtype: str
        """
        l_quote, string, r_quote = split_quotes(tok_val)

        # triple quoted string, follows normal string rules
        if len(l_quote) == 3:
            requoted = quote_string(string, style.string, 3)

        # empty string literal '' or ""
        elif len(l_quote) == 2:
            requoted = quote_string('', style.single_char, 1)

        # single character string literal 'a' or "a"
        elif (len(l_quote) == 1 and len(string) < 2
              and style.single_char.value not in string):
            requoted = quote_string(string, style.single_char, 1)

        # escaped single character string literal '\'a'
        elif (len(l_quote) == 1 and len(string) == 2 and string[0] == '\\'
              and style.single_char.value not in string):
            requoted = quote_string(string, style.single_char, 1)

        # other string literals like "abc"
        elif (len(l_quote) == 1 and len(string)
              and style.string.value not in string):
            requoted = quote_string(string, style.string, 1)

        else:
            # string doesn't need to be requoted
            requoted = tok_val

        return requoted

    with BytesIO(code.encode("utf-8")) as f:
        tokens = tokenize.tokenize(f.readline)
        new_tokens = []
        for tok in tokens:
            tok_num, tok_val, *_ = tok
            if tok_num == tokenize.STRING:
                requoted = requote_string_token(tok_val, style)
                new_tokens.append((tok_num, requoted, *_))
            else:
                new_tokens.append((tok_num, tok_val, *_))
    res: str | t.Any = tokenize.untokenize(new_tokens)

    if isinstance(res, bytes):
        return res.decode("utf-8")

    return res


def json_loader(json_str: str) -> t.Dict[str, str]:
    res: t.Dict[str, str] = dict(json.loads(json_str))
    return res


def toml_loader(toml_str: str) -> t.Dict[str, str]:
    return tomllib.loads(toml_str)


def load_conf(conf_file: str) -> QuoteStyle:
    """Load quoting style from given conf file"""

    loaders = {".json": json_loader, ".toml": toml_loader}

    style_file: Path = Path(conf_file)

    with open(style_file, 'r') as f:
        conf: str = f.read()

    style_dict = loaders[style_file.suffix](conf)
    style = QuoteStyle.from_dict(style_dict)
    return style


def get_style(name: str, conf_file: str) -> QuoteStyle:
    """Get quote style by name or from from conf file.
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


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()
    out = args.output
    results = {}

    # get style (builtin, custom)
    style: QuoteStyle = get_style(args.style, args.conf)

    # stdin
    if '-' in args.files:
        code: str = sys.stdin.read()
        content: str = requote_code(code, style)

        f_name: str = '-' if args.inplace else out
        results[f_name] = content

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
