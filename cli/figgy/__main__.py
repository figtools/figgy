# -*- coding: utf-8 -*-


"""bootstrap.__main__: executed when bootstrap directory is called as script."""

from figgy.entrypoint import cli

try:
    cli.main()
except Warning:
    pass