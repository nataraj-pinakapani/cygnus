#!/bin/bash
pip install -r requirements.txt
pip uninstall cygnus
pip install .
rm -rf build cygnus.egg-info dist
