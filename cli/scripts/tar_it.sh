#!/bin/bash

. scripts/utils.sh

version=$1

[[ -z "$version" ]] && die "Required parameter [version] is missing." || success "Making tar with version: $version"

mkdir -p "figgy/${version}/bin"

cp -R dist/__main__/* "figgy/${version}/bin/"

tar -czvf figgy.tar.gz "figgy/${version}/bin/"