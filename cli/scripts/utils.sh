#!/bin/bash

############## FORMATTING UTILS #################

# Useful formatting functions
reset=$(tput -T xterm-color sgr0)
red=$(tput -T xterm-color setaf 1)
green=$(tput -T xterm-color setaf 2)
yellow=$(tput -T xterm-color setaf 3)
blue=$(tput -T xterm-color setaf 4)

print() {
    printf "➜ %s\n" "$@"
}

warning() {
  printf "${yellow}⚠️ %s${reset}\n" "$@"
}

success() {
     printf "${green}✔︎ %s${reset}\n" "$@"
}

notify() {
    printf "${blue}➜ %s${reset}\n" "$@"
}

error() {
    printf "${red}✖ %s${reset}\n" "$@"
}

die () {
    error "$1"
    exit 1
}