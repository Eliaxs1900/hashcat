#!/bin/zsh
# show_case.sh <case> [NAME=VALUE ...]: what a screenshot of one case shows
cd /Users/Shared/hc5094-tests
print -P "%F{green}\$%f python3 run_case.py $*"
python3 -I run_case.py "$@"
