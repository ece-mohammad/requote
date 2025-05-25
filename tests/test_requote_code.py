#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import typing as t

import pytest

from requote.requote import (STYLES, QuoteChar, QuoteStyle, quote_string,
                             requote_code, split_quotes)


class TestSplitQuotes:
    """Tests split_quotes function with varying quote styles and edge cases."""

    @pytest.mark.parametrize(
        "string, expected",
        [
            # Empty input
            ("", ("", "", "")),
            # Testing strings with different quote styles
            ("'foo'", ("'", "foo", "'")),
            ('"foo"', ('"', "foo", '"')),
            ('"""foo"""', ('"""', "foo", '"""')),
            ("'''foo'''", ("'''", "foo", "'''")),
            # Empty strings
            ('""', ('""', "", '""')),
            ("''", ("''", "", "''")),
            ("''''''", ("''''''", "", "''''''")),
            ('""""""', ('""""""', "", '""""""')),
            # Single-character strings
            ("'a'", ("'", "a", "'")),
            ('"a"', ('"', "a", '"')),
            ("'''a'''", ("'''", "a", "'''")),
            ('"""a"""', ('"""', "a", '"""')),
            # Strings containing escape sequences
            ("'''\\a'''", ("'''", "\\a", "'''")),
            ('"""\\a"""', ('"""', "\\a", '"""')),
            # Strings with unescaped and escaped internal quotes
            ('"foo\'bar"', ('"', "foo'bar", '"')),
            ("'foo\"bar'", ("'", 'foo"bar', "'")),
            ("'foo\\\"bar'", ("'", 'foo\\"bar', "'")),
            ('"foo\\\'bar"', ('"', "foo\\'bar", '"')),
            ('"""foo\'bar"""', ('"""', "foo'bar", '"""')),
            ("'''foo\"bar'''", ("'''", 'foo"bar', "'''")),
            ("'''foo\\\"bar'''", ("'''", 'foo\\"bar', "'''")),
            ('"""foo\\\'bar"""', ('"""', "foo\\'bar", '"""')),
            ("'\"foo'\"bar'", ("'", '"foo\'"bar', "'")),
            # Edge cases with only quotes or prefixes
            ("'\"\"'", ("'", '""', "'")),
            ("'\\''", ("'", "\\'", "'")),
            ('"\\""', ('"', '\\"', '"')),
            ("\"''\"", ('"', "''", '"')),
            ("'''\"\"'''", ("'''", '""', "'''")),
            ('"""\'\'"""', ('"""', "''", '"""')),
            ("'''\"'''", ("'''", '"', "'''")),
            ("b'x'", ("", "b'x'", "")),
            ("u'x'", ("", "u'x'", "")),
            ("r'x'", ("", "r'x'", "")),
            ("f'x'", ("", "f'x'", "")),
            ("b'''x'''", ("", "b'''x'''", "")),
            ("u'''x'''", ("", "u'''x'''", "")),
            ("r'''x'''", ("", "r'''x'''", "")),
            ("f'''x'''", ("", "f'''x'''", "")),
            ('b"""x"""', ("", 'b"""x"""', "")),
            ('u"""x"""', ("", 'u"""x"""', "")),
            ('r"""x"""', ("", 'r"""x"""', "")),
            ('f"""x"""', ("", 'f"""x"""', "")),
            # No quotes
            ("example", ("", "example", "")),
            ("x", ("", "x", "")),
            ("", ("", "", "")),
            # Non-quote characters
            ("a = 'example'", ("", "a = 'example'", "")),
            # Whitespace handling
            ("' example '", ("'", " example ", "'")),
        ],
    )
    def test_split_quotes(self, string: str, expected: t.Tuple[str, str, str]) -> None:
        """Verify split_quotes function correctly splits quoted strings."""
        assert split_quotes(string) == expected


class TestQuoteString:
    """Tests for the quote_string function to ensure proper quoting."""

    @pytest.mark.parametrize(
        "string, quote_char, n_quotes, expected",
        [
            # Single quotes
            ("", QuoteChar.SINGLE_QUOTE, 1, "''"),
            ("a", QuoteChar.SINGLE_QUOTE, 1, "'a'"),
            ("foo", QuoteChar.SINGLE_QUOTE, 1, "'foo'"),
            # Double quotes
            ("", QuoteChar.DOUBLE_QUOTE, 1, '""'),
            ("a", QuoteChar.DOUBLE_QUOTE, 1, '"a"'),
            ("foo", QuoteChar.DOUBLE_QUOTE, 1, '"foo"'),
            # Triple quotes with single quote character
            ("", QuoteChar.SINGLE_QUOTE, 3, "''''''"),
            ("a", QuoteChar.SINGLE_QUOTE, 3, "'''a'''"),
            ("foo", QuoteChar.SINGLE_QUOTE, 3, "'''foo'''"),
            # Triple quotes with double quote character
            ("", QuoteChar.DOUBLE_QUOTE, 3, '""""""'),
            ("a", QuoteChar.DOUBLE_QUOTE, 3, '"""a"""'),
            ("foo", QuoteChar.DOUBLE_QUOTE, 3, '"""foo"""'),
            # Additional test cases
            (
                "long string with special chars @#$%",
                QuoteChar.SINGLE_QUOTE,
                1,
                "'long string with special chars @#$%'",
            ),
            # Verify special escape handling
            ("\t\n", QuoteChar.SINGLE_QUOTE, 1, "'\t\n'"),
            ("\t\n", QuoteChar.DOUBLE_QUOTE, 1, '"\t\n"'),
            ("\t\n", QuoteChar.SINGLE_QUOTE, 3, "'''\t\n'''"),
            ("\t\n", QuoteChar.DOUBLE_QUOTE, 3, '"""\t\n"""'),
        ],
    )
    def test_quote_string(
        self, string: str, quote_char: QuoteChar, n_quotes: int, expected: str
    ) -> None:
        """Verify quote_string function returns correctly quoted strings."""
        assert quote_string(string, quote_char, n_quotes) == expected


class TestRequoteCode:
    """Tests for the requote_code function, checking various quote conversion scenarios."""

    @pytest.mark.parametrize(
        "string, style, expected",
        [
            # Single character strings
            ("'c'", STYLES["c_style"], "'c'"),
            ('"c"', STYLES["c_style"], "'c'"),
            # Test regular strings using c_style
            ("'abc'", STYLES["c_style"], '"abc"'),
            ('"abc"', STYLES["c_style"], '"abc"'),
            # Test triple quoted strings using c_style
            ("'''abc'''", STYLES["c_style"], '"""abc"""'),
            ('"""abc"""', STYLES["c_style"], '"""abc"""'),
            # Empty string literals should follow single_char style
            ("''", STYLES["c_style"], "''"),
            ('""', STYLES["c_style"], "''"),
            # Strings containing internal quotes or escape sequences
            ('"\'"', STYLES["c_style"], '"\'"'),
            ("'\"'", STYLES["c_style"], "'\"'"),
            # Prefixed strings should remain unchanged
            ('b"foo"', STYLES["c_style"], 'b"foo"'),
            ('u"foo"', STYLES["c_style"], 'u"foo"'),
            ('r"foo"', STYLES["c_style"], 'r"foo"'),
            ('f"foo"', STYLES["c_style"], 'f"foo"'),
            # Test f-string expressions should remain unchanged
            ('f"{foo}"', STYLES["c_style"], 'f"{foo}"'),
            ("f\"{foo['x']}\"", STYLES["c_style"], "f\"{foo['x']}\""),
            # Multiline string handling should use triple_quoted style
            ('"foo\nbar"', STYLES["c_style"], '"foo\nbar"'),
            # Handling strings with escaped characters
            ('"foo\tbar"', STYLES["c_style"], '"foo\tbar"'),
            ('"foo\\\\bar"', STYLES["c_style"], '"foo\\\\bar"'),
            # Validate strings with escaped internal quotes
            ('"foo\'bar"', STYLES["c_style"], '"foo\'bar"'),
            ('"foo\\\'bar"', STYLES["c_style"], '"foo\\\'bar"'),
            ('"foo\\"bar"', STYLES["c_style"], '"foo\\"bar"'),
            # Empty string cases
            ("''", STYLES["c_style"], "''"),
            ('""', STYLES["c_style"], "''"),
            ("''''''", STYLES["c_style"], '""""""'),
            ('""""""', STYLES["c_style"], '""""""'),
            # Strings containing internal quotes or escape sequences
            ('"\'"', STYLES["c_style"], '"\'"'),
            ("'\"'", STYLES["c_style"], "'\"'"),
            ("'''\"'''", STYLES["c_style"], "'''\"'''"),
            ('"""\'"""', STYLES["c_style"], '"""\'"""'),
            # Strings composed only of quote marks
            ("'\"\"'", STYLES["c_style"], "'\"\"'"),
            ("'\\\"\\\"'", STYLES["c_style"], "'\\\"\\\"'"),
            # Prefixed strings (should remain unchanged)
            ('b"foo"', STYLES["c_style"], 'b"foo"'),
            ('u"foo"', STYLES["c_style"], 'u"foo"'),
            ('r"foo"', STYLES["c_style"], 'r"foo"'),
            ('f"foo"', STYLES["c_style"], 'f"foo"'),
            # Test that f-string expressions remain unchanged
            ('f"{foo}"', STYLES["c_style"], 'f"{foo}"'),
            ("f\"{foo['x']}\"", STYLES["c_style"], "f\"{foo['x']}\""),
        ],
    )
    def test_requote_code(self, string: str, style: QuoteStyle, expected: str) -> None:
        """Verify the requote_code function transforms input code correctly using c_style."""
        assert requote_code(string, style) == expected


if __name__ == "__main__":
    pytest.main()
