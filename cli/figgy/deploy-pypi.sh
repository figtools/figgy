#! /bin/sh

rm dist/*

source /Users/jordanmance/venv/figgy-homebrew/bin/activate

python setup.py sdist bdist_wheel

twine upload dist/* 
