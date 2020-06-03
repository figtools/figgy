#! /bin/sh

rm dist/* || echo "Dist already gone."

source /Users/jordanmance/venv/figgy-homebrew/bin/activate

python setup.py sdist bdist_wheel

twine upload dist/* 
