#!/usr/bin/env bash


SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"


echo $SCRIPTPATH
release=$("$SCRIPTPATH/get_version.sh")

echo "Found release: $release"

changelog_data=$(cat "$SCRIPTPATH/../CHANGELOG.md" | sed -E "s|.*(##\s*$release[^#]*)##\s+.*|\1|g")

echo $changelog_data