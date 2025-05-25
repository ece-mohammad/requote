#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test requote QuoteStyle class for style validation and conversion."""

import typing as t

import pytest

from requote.requote import STYLES, QuoteChar, QuoteStyle, ValidationError


class TestStyleValidation:
    """Test the QuoteStyle dataclass for valid and invalid configurations."""

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
    def test_valid_styles(self, single: str, string: str, triple: str) -> None:
        """Verify QuoteStyle handles valid styles."""
        style = QuoteStyle(
            single_char=QuoteChar(single),
            string=QuoteChar(string),
            triple_quoted=QuoteChar(triple),
        )
        assert style.single_char == QuoteChar(single)
        assert style.string == QuoteChar(string)
        assert style.triple_quoted == QuoteChar(triple)


class TestFromDict:
    """Test the QuoteStyle.from_dict method for various scenarios."""

    @pytest.mark.parametrize(
        "style_dict",
        [
            dict(single_char="'", string="'", triple_quoted="'"),
            dict(single_char='"', string='"', triple_quoted='"'),
            dict(single_char='"', string='"', triple_quoted="'"),
            dict(single_char='"', string="'", triple_quoted='"'),
            dict(single_char="'", string='"', triple_quoted='"'),
            dict(single_char='"', string="'", triple_quoted="'"),
            dict(single_char="'", string='"', triple_quoted="'"),
            dict(single_char="'", string="'", triple_quoted='"'),
        ],
    )
    def test_from_dict(self, style_dict: t.Dict[str, str]) -> None:
        """Verify from_dict processes valid quote configurations."""
        style = QuoteStyle.from_dict(style_dict)
        for key in style_dict:
            assert getattr(style, key) == QuoteChar(style_dict[key])

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
    def test_from_dict_missing_keys(self, style_dict: t.Dict[str,
                                                             str]) -> None:
        """Ensure from_dict raises ValidationError for missing keys."""
        with pytest.raises(ValidationError):
            _ = QuoteStyle.from_dict(style_dict)

    @pytest.mark.parametrize(
        "style_dict",
        [
            dict(single_char="-", string='"', triple_quoted='"'),
            dict(single_char="''", string="-", triple_quoted='"'),
            dict(single_char="''", string='"', triple_quoted="-"),
        ],
    )
    def test_from_dict_invalid_chars(self, style_dict: t.Dict[str,
                                                              str]) -> None:
        """Ensure from_dict raises ValidationError for invalid quote characters."""
        with pytest.raises(ValidationError):
            _ = QuoteStyle.from_dict(style_dict)

    @pytest.mark.parametrize(
        "style, style_dict",
        [
            # Default quote styles
            (
                QuoteStyle(
                    QuoteChar.SINGLE_QUOTE,
                    QuoteChar.DOUBLE_QUOTE,
                    QuoteChar.DOUBLE_QUOTE,
                ),
                dict(
                    single_char=QuoteChar.SINGLE_QUOTE.value,
                    string=QuoteChar.DOUBLE_QUOTE.value,
                    triple_quoted=QuoteChar.DOUBLE_QUOTE.value,
                ),
            ),
            # All single quotes
            (
                QuoteStyle(
                    QuoteChar.SINGLE_QUOTE,
                    QuoteChar.SINGLE_QUOTE,
                    QuoteChar.SINGLE_QUOTE,
                ),
                dict(
                    single_char=QuoteChar.SINGLE_QUOTE.value,
                    string=QuoteChar.SINGLE_QUOTE.value,
                    triple_quoted=QuoteChar.SINGLE_QUOTE.value,
                ),
            ),
            # All double quotes
            (
                QuoteStyle(
                    QuoteChar.DOUBLE_QUOTE,
                    QuoteChar.DOUBLE_QUOTE,
                    QuoteChar.DOUBLE_QUOTE,
                ),
                dict(
                    single_char=QuoteChar.DOUBLE_QUOTE.value,
                    string=QuoteChar.DOUBLE_QUOTE.value,
                    triple_quoted=QuoteChar.DOUBLE_QUOTE.value,
                ),
            ),
            # Mixed quotes
            (
                QuoteStyle(
                    QuoteChar.DOUBLE_QUOTE,
                    QuoteChar.SINGLE_QUOTE,
                    QuoteChar.SINGLE_QUOTE,
                ),
                dict(
                    single_char=QuoteChar.DOUBLE_QUOTE.value,
                    string=QuoteChar.SINGLE_QUOTE.value,
                    triple_quoted=QuoteChar.SINGLE_QUOTE.value,
                ),
            ),
            (
                QuoteStyle(
                    QuoteChar.SINGLE_QUOTE,
                    QuoteChar.SINGLE_QUOTE,
                    QuoteChar.DOUBLE_QUOTE,
                ),
                dict(
                    single_char=QuoteChar.SINGLE_QUOTE.value,
                    string=QuoteChar.SINGLE_QUOTE.value,
                    triple_quoted=QuoteChar.DOUBLE_QUOTE.value,
                ),
            ),
            (
                QuoteStyle(
                    QuoteChar.DOUBLE_QUOTE,
                    QuoteChar.DOUBLE_QUOTE,
                    QuoteChar.SINGLE_QUOTE,
                ),
                dict(
                    single_char=QuoteChar.DOUBLE_QUOTE.value,
                    string=QuoteChar.DOUBLE_QUOTE.value,
                    triple_quoted=QuoteChar.SINGLE_QUOTE.value,
                ),
            ),
        ],
    )
    def test_to_dict(self, style: QuoteStyle, style_dict: t.Dict[str,
                                                                 str]) -> None:
        """Check QuoteStyle.to_dict matches expected dictionary."""
        assert style.to_dict() == style_dict


class TestBuiltinStyles:
    """Test the retrieval and handling of builtin styles by name."""

    @pytest.mark.parametrize(
        "style_name",
        (
            "black",
            "c_style",
        ),
    )
    def test_builtin_styles(self, style_name: str) -> None:
        """Verify that builtin styles are accessible and valid."""
        assert STYLES[
            style_name], f"Style {style_name} should exist as a valid style."

    def test_unknown_styles(self) -> None:
        """Ensure accessing an unknown style raises KeyError."""
        with pytest.raises(KeyError):
            _ = STYLES["FooBar"]
