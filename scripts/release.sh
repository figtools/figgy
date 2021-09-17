#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

version=$($SCRIPTPATH/get_version.sh)
git tag -fa "v$version" -m "Tagging commit" && git push origin --tags