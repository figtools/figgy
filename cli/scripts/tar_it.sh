#!/bin/bash
version=$1

echo "Making tar with version: $version"

mkdir -p "figgy/${version}/bin"

cp -R dist/__main__/* "figgy/${version}/bin/"
tar -czvf figgy.tar.gz figgy/${version}/bin
