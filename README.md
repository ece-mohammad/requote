# Requote

A command line tool that unifies string quotes through python code.

## Why

I'll give you a better one, Why not?

Coming from `C/C++` to `Python`, I prefer using single quotes for single character string literals. But sometimes I use double quotes as well. AFAIK, formatters don't differentiate between single character string literals and longer strings, and apply the same quoting strategy for all of them. I wanted something different, and well, here we are.

## Usage

Pretty straight forward, I tried to follow `clang-format` style

```bash
usage: requote.py [-h] [-i | -o OUTPUT] [-s {black,c_style} | -c CONF] [files ...]

Requote

positional arguments:
  files                 Input python files to requote, can be a single file, or multiple files, or from stdin (using '-'). Can't read from both stdin and files at the same time. Default: reads from stdin

options:
  -h, --help            show this help message and exit
  -i, --inplace         modify files in place. Can't be used with -o OUTPUT. Default: False
  -o OUTPUT, --output OUTPUT
                        file to write the output, use '-' to write to stdout. Can't be used with -i. Default: write to stdout
  -s {black,c_style}, --style {black,c_style}
                        quoting style to use. Can't be used with -c CONF. Default: black
  -c CONF, --conf CONF  path to a {json,toml} configuration file that contains custom style settings Can't be used with -s STYLE. Default: None
```

## Install

- pull repository

```bash
git pull git@github.com:ece-mohammad/requote.git

```

- use it directly, there are not third party requirements

```bash
python requote foo.py -i
```

- If you're on Linux, you can make an alias in your `~/.bash_aliases` or `~/.bash_rc` files:

```bash
alias requote="python path/to/requote.py"
```
