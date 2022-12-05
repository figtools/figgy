#!/usr/bin/env bash

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cat "$SCRIPTPATH/../terraform/_other_cfgs.tf"| grep -E "version\s+=\s+" | sed -E "s#.*([0-9]+.[0-9]+.[0-9]+[a-zA-Z]?).*#\1#g"