#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test QuoteChar enum class from the requote module.

These tests cover checking that only valid quote characters can be
used to instantiate the QuoteChar enum, and that invalid characters
raise the appropriate exception.
"""

import pytest

from requote.requote import QuoteChar


class TestQuoteChar:
    """Test that QuoteChar enum accepts only valid quote chars: ' and " """

    @pytest.mark.parametrize(
        "quote_char, expected",
        [
            (QuoteChar.SINGLE_QUOTE, QuoteChar.SINGLE_QUOTE),
            (QuoteChar.DOUBLE_QUOTE, QuoteChar.DOUBLE_QUOTE),
            ("'", QuoteChar.SINGLE_QUOTE),
            ('"', QuoteChar.DOUBLE_QUOTE),
        ],
    )
    def test_valid_quote_chars(self, quote_char: str,
                               expected: QuoteChar) -> None:
        """ensure valid quote chars are handled correctly"""
        assert QuoteChar(quote_char) == expected

    @pytest.mark.parametrize(
        "quote_char",
        [
            # punctuation, digits and alpha
            "1",
            "a",
            "+",
            "-",
            "`",
            # multiple quotes
            "'''",
            '"""',
        ],
    )
    def test_invalid_quote_chars(self, quote_char: str) -> None:
        """ensure invalid quote chars raise ValueError"""
        with pytest.raises(ValueError):
            QuoteChar(quote_char)
