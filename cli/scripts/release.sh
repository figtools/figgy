#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
version=$(cat "$SCRIPTPATH/../figcli/config/constants.py"| grep -E "VERSION\s+=\s+" | grep -v "AUDIT" | sed -E "s#.*([0-9]+.[0-9]+.[0-9]+[a-zA-Z]?).*#\1#g")

git tag -fa "v$version" -m "Tagging commit" && git push origin --tags