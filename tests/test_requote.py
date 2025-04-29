import pytest

from requote import (QuoteChar, Styles, get_style, json_loader, load_conf,
                     quote_string, requote_code, split_quotes, toml_loader)


# TODO: test style validation
class TestStyleValidation:
    ...


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
            ("'foo\"bar'", ("'", "foo\"bar", "'")),
            ('"foo\'bar"', ('"', "foo\'bar", '"')),
            ("'foo\\\"bar'", ("'", "foo\\\"bar", "'")),
            ('"foo\\\'bar"', ('"', "foo\\\'bar", '"')),

            # string of quotes only
            ("'\"\"'", ("'", '""', "'")),
            ('"\'\'"', ('"', "''", '"')),
        ])
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
        ])
    def test_quote_string(self, input, quote_char, n_quotes, expected):
        assert quote_string(input, quote_char, n_quotes) == expected


# test requoting
class TestRequoteCode:

    @pytest.mark.parametrize("input, style, expected", [])
    def test_requote_code_black_style(self, input, style, expected):
        assert requote_code(input, style) == expected


# TODO: test configuration parsing & loading

# TODO: test configuration loading from files

# TODO: test reading from stdin
