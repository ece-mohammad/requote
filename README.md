# Requote

A command line tool that unifies string quotes through python code.

## Why

I'll give you a better one, Why not?

Coming from `C/C++` to `Python`, I prefer using single quotes for 
single character string literals. But someimes I use double quotes
as well.
AFAIK, formatters don't diffrentiate between single character string
literals and longer strings, and apply the same quoting strategy for
all of them.
I wanted something different, and well, here we are.

## Usage

Pretty straight forward, I tried to follow `clang-format` cli style

```bash
usage: requote.py [-h] [-i | -o OUTPUT] [-s {black,c_style} | -c CONF] [files ...]

Requote

positional arguments:
  files                 Input pythopn files to requote, can be a single file, or multiple files. Default: reads from stdin

options:
  -h, --help            show this help message and exit
  -i, --inplace         modify files in place.
  -o OUTPUT, --output OUTPUT
                        file to write the output. Default: write to stdout
  -s {black,c_style}, --style {black,c_style}
                        quoting style to use. Default: black.
  -c CONF, --conf CONF  path to a {yaml,json,toml} configuration file that contains custom style settings
```

## Install

- pull repository

```bash
git pull git@github.com:ece-mohammad/requote.git

```

- install requirements

```bash
cd requote
python -m virtualenv .venv
. ./.venv/bin/activate
pip install -r requirements.txt
```

- use it

```
python requote foo.py -i
```

