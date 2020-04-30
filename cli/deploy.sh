#!/usr/bin/env bash

# This script sets the latest build to a newly defined version. After this script is run, all running figgys out there
# will be prompted to auto-update. So make sure this is a stable version!

# Ensure that the VERSION parameter has been updated in config.py with the new version # you want to deploy.
# Also ensure that VERSION has been committed so it will be built / deployed.
reset=$(tput -T xterm-color sgr0)
red=$(tput -T xterm-color setaf 1)
green=$(tput -T xterm-color setaf 2)
blue=$(tput -T xterm-color setaf 4)

die() {
    e_error "$1"
    exit 1
}

e_error() {
    printf "${red}✖ %s${reset}\n" "$@" >&2
}

e_notify() {
    printf "${blue}➜ %s${reset}\n" "$@"
}

e_notify "Make sure all your code has been committed and a build completed before running this deploy script."
e_notify "Make sure to run figgy iam export --env mgmt first as well!"

version=$(cat config.py | grep -E "^VERSION =" | sed -E "s#.*=.*'([0-9]+\.[0-9]+\.[0-9]+)'.*#\1#g")
current_version=$(aws ssm get-parameter --name /devops/devops-ci/figgy/latest-version | jq -r '.Parameter.Value')

echo "$current_version -> $version"

if [ "$current_version" = "$version" ]; then
    e_error "Deployed Version ($current_version) is the same as the config.py defined verison of $version. Either this version has already been deployed, or you forgot to update the config.py VERSION property."
    e_notify "Don't forget, you MUST COMMIT the updated version and let the build complete BEFORE running this script."
    exit 1
fi

echo "Found existing version: $current_version"
echo "Deploying figgy with new version: $version"
read -e -p "Continue? (Y/N): " continue

if [ "$continue" != "Y" ] && [ "$continue" != "y" ]; then
    exit 1
fi


aws s3 cp "s3://old-bucket-name/figgy/latest/windows/figgy.exe" "s3://old-bucket-name/figgy/${version}/windows/figgy.exe" || die "Error copying figgy windows version."
aws s3 cp "s3://old-bucket-name/figgy/latest/linux/figgy" "s3://old-bucket-name/figgy/${version}/linux/figgy"  || die "Error copying figgy linux version."
aws s3 cp "s3://old-bucket-name/figgy/latest/darwin/figgy" "s3://old-bucket-name/figgy/${version}/darwin/figgy" || die "Error copying figgy darwin version."
aws s3 cp "s3://old-bucket-name/figgy/latest/darwin/figgy.zip" "s3://old-bucket-name/figgy/${version}/darwin/figgy.zip" || die "Error copying figgy.zip darwin version."
aws ssm put-parameter --name /devops/devops-ci/figgy/latest-version --type "String" --value "$version" --overwrite || die "Error updating figgy version in ParameterStore"
