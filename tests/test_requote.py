#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from requote import (QuoteChar, QuoteStyle, Styles, ValidationError, get_style,
                     json_loader, load_conf, quote_string, requote_code,
                     split_quotes, toml_loader)

# TODO: test configuration parsing & loading

# TODO: test configuration loading from files

# TODO: test reading from stdin


class TestQuoteChar:

    @pytest.mark.parametrize(
        "quote_char, expected",
        [
            (QuoteChar.SINGLE_QUOTE, QuoteChar.SINGLE_QUOTE),
            (QuoteChar.DOUBLE_QUOTE, QuoteChar.DOUBLE_QUOTE),
            ("'", QuoteChar.SINGLE_QUOTE),
            ('"', QuoteChar.DOUBLE_QUOTE),
        ],
    )
    def test_valid_quote_chars(self, quote_char: str, expected: QuoteChar):
        assert QuoteChar(quote_char) == expected

    @pytest.mark.parametrize(
        "quote_char",
        [
            # punctuation, digits and alpha
            '1',
            'a',
            '+',
            '-',
            '`',
            # multiple quotes
            "'''",
            '"""',
        ],
    )
    def test_invalid_quote_chars(self, quote_char: str):
        with pytest.raises(ValueError):
            QuoteChar(quote_char)


class TestStyleValidation:

    @pytest.mark.parametrize(
        "single, string, triple",
        [
            # valid values
            ("'", "'", "'"),
            ('"', '"', '"'),
            ('"', '"', "'"),
            ('"', "'", '"'),
            ("'", '"', '"'),
            ('"', "'", "'"),
            ("'", '"', "'"),
            ("'", "'", '"'),
        ],
    )
    def test_valid_styles(self, single: str, string: str, triple: str):
        assert QuoteStyle(
            single_char=QuoteChar(single),
            string=QuoteChar(string),
            triple_quoted=QuoteChar(triple),
        )

    @pytest.mark.parametrize(
        "style_dict",
        [
            dict(single_char="'", string='"', triple_quoted='"'),
        ],
    )
    def test_from_dict(self, style_dict):
        assert QuoteStyle.from_dict(style_dict)

    @pytest.mark.parametrize(
        "style_dict",
        [
            dict(single_char="'"),
            dict(string='"'),
            dict(triple_quoted='"'),
            dict(single_char="'", string='"'),
            dict(single_char="'", triple_quoted='"'),
            dict(string='"', triple_quoted='"'),
        ],
    )
    def test_from_dict_missing_keys(self, style_dict):
        with pytest.raises(KeyError):
            assert QuoteStyle.from_dict(style_dict)

    @pytest.mark.parametrize(
        "style_dict",
        [
            dict(single_char='-', string='"', triple_quoted='"'),
            dict(single_char="''", string='-', triple_quoted='"'),
            dict(single_char="''", string='"', triple_quoted='-'),
        ],
    )
    def test_from_dict_invalid_chars(self, style_dict):
        with pytest.raises(ValueError):
            assert QuoteStyle.from_dict(style_dict)


class TestBuiltinStyles:

    @pytest.mark.parametrize(
        "style_name",
        (
            "black",
            "c_style",
        ),
    )
    def test_builtin_styles(self, style_name: str):
        assert Styles[style_name]

    def test_unknown_styles(self):
        with pytest.raises(KeyError):
            Styles["FooBar"]


# test split quotes
class TestSplitQuotes:

    @pytest.mark.parametrize(
        "input, expected",
        [
            # single quoted string
            ("'foo'", ("'", "foo", "'")),
            # double quoted string
            ('"foo"', ('"', "foo", '"')),
            # triple quoted string
            ('"""foo"""', ('"""', "foo", '"""')),
            ("'''foo'''", ("'''", "foo", "'''")),
            # empty string
            ('""', ('""', '', '""')),
            ("''", ("''", '', "''")),
            # single char string
            ("'a'", ("'", 'a', "'")),
            ('"a"', ('"', 'a', '"')),
            # string with escape sequence
            ("'\\a'", ("'", "\\a", "'")),
            ('"\\a"', ('"', "\\a", '"')),
            # string with quotes
            ("'foo'bar'", ("'", "foo'bar", "'")),
            ('"foo"bar"', ('"', 'foo"bar', '"')),
            # string with escaped quotes
            ("'foo\"bar'", ("'", 'foo"bar', "'")),
            ('"foo\'bar"', ('"', "foo'bar", '"')),
            ("'foo\\\"bar'", ("'", 'foo\\"bar', "'")),
            ('"foo\\\'bar"', ('"', "foo\\'bar", '"')),
            # string of quotes only
            ("'\"\"'", ("'", '""', "'")),
            ("\"''\"", ('"', "''", '"')),
            # prefixed strings are skipped (b"", r"", u"", f"")
            ("b'x'", ('', "b'x'", '')),
            ("u'x'", ('', "u'x'", '')),
            ("r'x'", ('', "r'x'", '')),
            ("f'x'", ('', "f'x'", '')),
        ],
    )
    def test_split_quotes(self, input, expected):
        assert split_quotes(input) == expected


class TestQuoteString:

    @pytest.mark.parametrize(
        "input, quote_char, n_quotes, expected",
        [
            # single quotes
            # empty string
            ('', QuoteChar.SINGLE_QUOTE, 1, "''"),
            ('', QuoteChar.DOUBLE_QUOTE, 1, '""'),
            # single character string
            ('a', QuoteChar.SINGLE_QUOTE, 1, "'a'"),
            ('a', QuoteChar.DOUBLE_QUOTE, 1, '"a"'),
            # string
            ("foo", QuoteChar.SINGLE_QUOTE, 1, "'foo'"),
            ("foo", QuoteChar.DOUBLE_QUOTE, 1, '"foo"'),
            # triple quotes
            # empty string
            ('', QuoteChar.SINGLE_QUOTE, 3, "''''''"),
            ('', QuoteChar.DOUBLE_QUOTE, 3, '""""""'),
            # single character string
            ('a', QuoteChar.SINGLE_QUOTE, 3, "'''a'''"),
            ('a', QuoteChar.DOUBLE_QUOTE, 3, '"""a"""'),
            # string
            ("foo", QuoteChar.SINGLE_QUOTE, 3, "'''foo'''"),
            ("foo", QuoteChar.DOUBLE_QUOTE, 3, '"""foo"""'),
        ],
    )
    def test_quote_string(self, input, quote_char, n_quotes, expected):
        assert quote_string(input, quote_char, n_quotes) == expected


# test requoting
class TestRequoteCode:

    @pytest.mark.parametrize(
        "input, style, expected",
        [
            # single char
            ("'c'", Styles["c_style"], "'c'"),
            ('"c"', Styles["c_style"], "'c'"),
            # string
            ("'abc'", Styles["c_style"], '"abc"'),
            ('"abc"', Styles["c_style"], '"abc"'),
            # triple quoted
            ("'''abc'''", Styles["c_style"], '"""abc"""'),
            ('"""abc"""', Styles["c_style"], '"""abc"""'),
            # empty string
            ("''", Styles["c_style"], "''"),
            ('""', Styles["c_style"], "''"),
            pytest.param("''''''",
                         Styles["c_style"],
                         '""""""',
                         marks=pytest.mark.xfail(
                             reason="bug in triple quoted empty strings")),
            ('""""""', Styles["c_style"], '""""""'),
            # string containing quotes
            ('"\'"', Styles["c_style"], '"\'"'),
            ("'\"'", Styles["c_style"], "'\"'"),
            pytest.param(
                "'''\"'''",
                Styles["c_style"],
                "'''\"'''",
                marks=pytest.mark.xfail(
                    reason="bug in triple quoted strings that contain a quote")
            ),
            ('"""\'"""', Styles["c_style"], '"""\'"""'),
            # string of quotes
            ("'\"\"'", Styles["c_style"], "'\"\"'"),
            # prefixed string
            ('b"foo"', Styles["c_style"], 'b"foo"'),
            ('u"foo"', Styles["c_style"], 'u"foo"'),
            ('r"foo"', Styles["c_style"], 'r"foo"'),
            ('f"foo"', Styles["c_style"], 'f"foo"'),
            # f-strings with expressions
            ('f"{foo}"', Styles["c_style"], 'f"{foo}"'),
            ('f"{foo[\'x\']}"', Styles["c_style"], 'f"{foo[\'x\']}"'),
            # multiline string
            ('"foo\nbar"', Styles["c_style"], '"foo\nbar"'),
            # strings with escaped chars
            ('"foo\tbar"', Styles["c_style"], '"foo\tbar"'),
            ('"foo\\\\bar"', Styles["c_style"], '"foo\\\\bar"'),
            # strings with escaped quotes
            ('"foo\'bar"', Styles["c_style"], '"foo\'bar"'),
            ('"foo\'bar"', Styles["c_style"], '"foo\'bar"'),
            ('"foo\\\'bar"', Styles["c_style"], '"foo\\\'bar"'),
            ('"foo\\\"bar"', Styles["c_style"], '"foo\\\"bar"'),
        ])
    def test_requote_code_black_style(self, input, style, expected):
        assert requote_code(input, style) == expected
