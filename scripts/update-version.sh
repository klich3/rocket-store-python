#!/bin/bash
#
#
#█▀ █▄█ █▀▀ █░█ █▀▀ █░█
#▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀
#
#Author: <Anton Sychev> (anton at sychev dot xyz) 
#update-version.sh (c) 2024 
#Created:  2024-01-10 21:30:07 
#Desc: update version before release
#

version=$(grep 'version =' pyproject.toml | cut -d '"' -f 2)

echo "Current version: $version"

major=$(echo $version | cut -d '.' -f 1)
minor=$(echo $version | cut -d '.' -f 2)
patch=$(echo $version | cut -d '.' -f 3)

patch=$((patch + 1))

new_version="$major.$minor.$patch"

echo "New version: $new_version"

# update src/__version__.py
sed -i "" "s/__version__ = \".*\"/__version__ = \"$new_version\"/g" src/Rocketstore/__version__.py

# update CITATION.cff
sed -i "" "/cff-version:/!s/version: .*/version: $new_version/g" CITATION.cff

# update pyproject.toml
sed -i "" "s/version = \".*\"/version = \"$new_version\"/g" pyproject.toml