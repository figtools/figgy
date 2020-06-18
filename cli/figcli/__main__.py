# -*- coding: utf-8 -*-


"""bootstrap.__main__: executed when bootstrap directory is called as script."""

from figcli.entrypoint import cli

try:
    cli.main()
except Warning:
    pass