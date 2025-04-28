import pytest

from requote import (get_style, json_loader, load_conf, quote_string,
                     read_stdin, requote_code, split_quotes, toml_loader)

# test quoting quoting


# test split quotes
class TestSplitQuotes:

    def test_split_single_quote_string(self):
        assert split_quotes("'foo'") == ("'", "foo", "'")


# test requoting
class TestRequoteCode:
    ...


# test configuration parsing

# test configuration loading from files

# test reading from stdin
