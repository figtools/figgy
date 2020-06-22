#!/bin/bash

. scripts/utils.sh

version=$1

[[ -z "$version" ]] && die "Required parameter [version] is missing." || success "Creating release tag for version: $version"


git tag -fa "v$version" -m "Tagging commit" && git push origin --tags