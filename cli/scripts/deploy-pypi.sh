#! /bin/sh

rm dist/* || echo "Dist already gone."

python setup.py sdist bdist_wheel

twine upload dist/* 
