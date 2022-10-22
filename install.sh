#!/bin/bash
pip install -r requirements.txt
pip uninstall Cygnus
pip uninstall cygnus
python3 setup.py install
