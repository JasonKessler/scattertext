#!/usr/bin/env bash

rm dist/*
python setup.py sdist bdist_wheel
twine upload dist/*
source activate py2
rm dist/*
python setup.py sdist bdist_wheel
twine upload dist/*py2*
source deactivate
