#!/usr/bin/env bash
cd doc
sphinx-apidoc -o source/ ../scattertext
sphinx-build source/ ../docs
