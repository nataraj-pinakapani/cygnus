#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 10:40:09 2022

@author: nataraj
"""

from cygnus import _FindNoiseContributors_


# =============================================================================
# Comment1:
# _FindNoiseContributors_ Usage:
# ------------------------------
# _FindNoiseContributors_ (<str:rawfile_name>, <integer:num_of_contributors>,\
#   [<str:rawfile path>])
# rawfilepath is optional. If not specified, the script will search for file in
# /$HOME/.xschem/simulations/
# 
# To create a raw binary file from noise simulation, add the following commands
# in the .control block in ngspice
#
# noise v(vout) V6 dec 10 1kHz 100MEG 1 *<== must add 1 after 100MEG
# setplot noise2
# write ldo_2_noise.raw
#
# 
# =============================================================================
_FindNoiseContributors_(rawfile='ldo_2_noise.raw', num_of_contributors=30)