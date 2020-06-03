#!/bin/sh

source ~/venv/figgy-homebrew/bin/virtualenvwrapper.sh

mktmpenv

pip install figgy-cli homebrew-pypi-poet

poet figgy-cli

deactivate