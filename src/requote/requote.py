#!/usr/bin/env python3
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

To make the tool as flexible as possible, a style has 3 options:
    1. single character string: single or double quotes.
    2. single line strings: single or double quotes.
    3. triple_quoted: single or double triple quotes (should be double
        quotes according to pep8)

Quotes aren't changed for:
    - anywhere outside a string literals like comments
    - strings that contain the same quote character as the surrounding quotes
    - f-strings


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
from pathlib import Path

__version__ = "1.0.0"


class ValidationError(Exception):
    """Quote style validation error"""


class QuoteChar(enum.Enum):
    """An enum type to give names for quoting chars:
    - SINGLE_QUOTE = "'"
    - DOUBLE_QUOTE = '"'
    """

    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'

    @property
    def escaped(self) -> str:
        """Get quote char as an escaped string"""
        return f"\\{self.value}"

    @property
    def other(self) -> "QuoteChar":
        """Return other quote char"""
        if self == QuoteChar.SINGLE_QUOTE:
            return QuoteChar.DOUBLE_QUOTE
        return QuoteChar.SINGLE_QUOTE


@dataclass()
class QuoteStyle:
    """A data class that represents a quoting style.

    It has the following variables:
    - single_char: quote character for single character and empty strings
    - string: quote character for strings
    - triple_quoted: quote character for triple quoted strings

    Default values for quote style:
    - single_char: single quote `'`
    - string: double quote `"`
    - triple_quoted: double quote `"`

    Each of the variables must be either a singe quote `'`, or a double quote
    character `"`, or an enum of `QuoteChar`.

    static methods:
    - validate(style: t.Dict[str, str]) -> None: validates a quote style dict
    - _is_valid_quote(quote: str | QuoteChar) -> bool: a helper function that
    checks that given quote is a valid quote
    -

    class methods:
    - from_dict(style: t.Dict[str, str]) -> QuoteStyle: returns a QuoteStyle
    object from given quote style dict

    methods:
    - to_dict() -> Dict[str, str]: returns a dict representation of a quote
    style object
    """

    single_char: QuoteChar = QuoteChar.SINGLE_QUOTE
    string: QuoteChar = QuoteChar.DOUBLE_QUOTE
    triple_quoted: QuoteChar = QuoteChar.DOUBLE_QUOTE

    def __post_init__(self) -> None:
        self.validate(self.to_dict())

    @staticmethod
    def _is_valid_quote(quote: str | QuoteChar) -> bool:
        """Check that give quote is a valid quote char"""
        try:
            QuoteChar(quote)
        except ValueError:
            return False
        return True

    @staticmethod
    def validate(style: t.Dict[str, str]) -> None:
        """Validates a style dictionary.

        Examples:

            >>> QuoteStyle.validate(
            ...     {
            ...         "single_char": "'",
            ...         "string": "'",
            ...         "triple_quoted: '"',
            ...     }
            ... )

            >>> QuoteStyle.validate(
            ...     {
            ...         "single_char": QuoteChar."'",
            ...     }
            ... )
            >>> ValidationError

            >>> QuoteStyle.validate(
            ...     {
            ...         "string": QuoteChar."'",
            ...     }
            ... )
            >>> ValidationError

            >>> QuoteStyle.validate(
            ...     {
            ...         "single_char": "(",
            ...         "string": "'",
            ...     }
            ... )
            >>> ValidationError

        :param style: a quoting style dictionary that contains the
            quote characters for different strings. A style if valid iff it
            satisfies the following conditions
                1. contains the keys: single_char and string.
                2. the values for both of them are either
                a single quote or a double quote character.
        :type style: Dict[str, str]
        :raises ValidationError: if the style dictionary doesn't satisfy the
        validation criteria:
        1. style dict doesn't contain all style keys {"single_char", "string",
            "triple_quoted"}
        2. all style values are valid quote chars QuoteChar.SINGLE_QUOTE or
        """
        # validate keys
        required_keys = {"single_char", "string", "triple_quoted"}
        missing_keys = required_keys - style.keys()
        if missing_keys:
            raise ValidationError(f"Missing keys in style: {style}")

        # validate values
        for key in required_keys:
            quote = style[key]
            if not QuoteStyle._is_valid_quote(quote):
                raise ValidationError(f"Invalid quote char for {key}: {quote}")

    @classmethod
    def from_dict(cls, style: t.Dict[str, str]) -> "QuoteStyle":
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
        cls.validate(style)
        return QuoteStyle(
            single_char=QuoteChar(style["single_char"]),
            string=QuoteChar(style["string"]),
            triple_quoted=QuoteChar(style["triple_quoted"]),
        )

    def to_dict(self) -> t.Dict[str, str]:
        """Convert quote style object into a dictionary"""
        return {
            "single_char": self.single_char.value,
            "string": self.string.value,
            "triple_quoted": self.triple_quoted.value,
        }

    def __str__(self) -> str:
        return (
            f"single_char: {self.single_char.value}, "
            f"string: {self.string.value}, "
            f"triple_quoted: {self.triple_quoted.value}"
        )


# default styles
STYLES: t.Final[t.Dict[str, QuoteStyle]] = {
    "black": QuoteStyle(
        single_char=QuoteChar.DOUBLE_QUOTE,
        string=QuoteChar.DOUBLE_QUOTE,
        triple_quoted=QuoteChar.DOUBLE_QUOTE,
    ),
    "c_style": QuoteStyle(
        single_char=QuoteChar.SINGLE_QUOTE,
        string=QuoteChar.DOUBLE_QUOTE,
        triple_quoted=QuoteChar.DOUBLE_QUOTE,
    ),
}


def get_parser() -> argparse.ArgumentParser:  # pragma: no cover
    """initialize ArgumentParser instance"""
    parser = argparse.ArgumentParser(description="Requote")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        help="print version and exit",
        version=f"%(prog)s {__version__}",
    )
    # input
    parser.add_argument(
        "files",
        help="""Input python files to requote, can be a single file,
                or multiple files, or from stdin (using '-'). Can't read
                from both stdin and files at the same time.
                Default: reads from stdin""",
        type=str,
        nargs="*",
        default=["-"],
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
        default="-",
    )
    # style
    style = parser.add_mutually_exclusive_group()
    style.add_argument(
        "-s",
        "--style",
        choices=tuple(STYLES.keys()),
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
    """Remove surrounding quote characters from a string."""
    stripped = string.strip()

    if not stripped:
        return ("", string, "")  # Handle empty string case

    leader = stripped[0]
    supported_quotes = {i.value for i in QuoteChar}

    if leader not in supported_quotes:
        return ("", string, "")  # No quotes to remove

    n_quotes = len(stripped) - len(stripped.lstrip(leader))
    quotes = leader * n_quotes
    return quotes, stripped[n_quotes:-n_quotes], quotes


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

        # empty string
        match split_quotes(tok_val):
            case ("''", "", "''") | ('""', "", '""'):
                requoted = quote_string("", style.single_char)

            case ("''''''", "", "''''''") | ('""""""', "", '""""""'):
                requoted = quote_string("", style.string, 3)

            # normal string
            case ("'", string, "'") | ('"', string, '"'):
                # string is a single quote
                if string == style.single_char.value:
                    requoted = tok_val

                # single char
                elif len(string) == 1:
                    requoted = quote_string(string, style.single_char)

                # contains unescaped style's string quote
                elif string.count(style.string.value):
                    requoted = tok_val

                else:
                    requoted = quote_string(string, style.string)

            # triple quoted
            case ("'''", string, "'''") | ('"""', string, '"""'):
                # string is a single quote chat
                if string == style.triple_quoted.value:
                    requoted = tok_val

                elif string.startswith(style.triple_quoted.value):
                    requoted = tok_val

                elif string.endswith(style.triple_quoted.value):
                    requoted = tok_val

                else:
                    requoted = quote_string(string, style.triple_quoted, 3)

            case _:
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

    res = tokenize.untokenize(new_tokens)

    if isinstance(res, bytes):
        return res.decode("utf-8")

    return str(res)


def json_loader(json_str: str) -> t.Dict[str, str]:
    """load configuration from json string"""
    res: t.Dict[str, str] = dict(json.loads(json_str))
    return res


def toml_loader(toml_str: str) -> t.Dict[str, str]:
    """load configuration from toml string"""
    return tomllib.loads(toml_str)


def load_conf(conf_file: str) -> QuoteStyle:
    """Load quoting style from given conf file"""

    loaders = {".json": json_loader, ".toml": toml_loader}

    style_file: Path = Path(conf_file)

    with open(style_file, "r", encoding="utf-8") as f:
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
        return STYLES[name]

    try:
        style: QuoteStyle = load_conf(conf_file)

    except ValidationError:
        print(
            f"Invalid style in given conf file: {conf_file}", file=sys.stderr
        )
        sys.exit(1)

    return style


def main() -> None:
    """Main entry point of requote CLI"""
    parser = get_parser()
    args = parser.parse_args()
    out = args.output
    results: t.Dict[str, t.List[str]] = {}

    # get style (builtin, custom)
    style: QuoteStyle = get_style(args.style, args.conf)

    # stdin
    if "-" in args.files:
        code: str = sys.stdin.read()
        content: str = requote_code(code, style)

        f_name: str = "-" if args.inplace else out
        results[f_name] = [content]

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
            print(
                f"given file is not a python file: {src_file}", file=sys.stderr
            )
            sys.exit(1)

        with open(src_file, "r", encoding="utf-8") as src:
            code = src.read()

        content = requote_code(code, style)

        if args.inplace:
            results[f] = [content]

        else:
            results[out] = results.get(out, [])
            results[out].append(content)

    # write results
    for f, res in results.items():
        concat = "\n".join(res)
        if f == "-":
            print(concat)
        else:
            with open(f, "w", encoding="utf-8") as outfile:
                outfile.write(concat)


if __name__ == "__main__":
    main()
