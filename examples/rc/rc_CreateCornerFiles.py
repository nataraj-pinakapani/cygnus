#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 10:40:09 2022

@author: nataraj
"""

from cygnus import _CreateCornerSimFiles_


# =============================================================================
# _CreateCornerSimFiles_ Usage:
# ------------------------------
# Specify the following variables
# model_file --> SPice Model File Full Path
# sim_dir --> Full path of Sim Dir. <Must have testbench file
# tb --> testbenchfile name
# corners Eg: corners={'lib':['ff','ss'],'RLOAD':[1e3,1e4]}
# lib is a must have input. If you want to run only tt, specify just 'tt'
# Other devices must be defined in the test bench
# _CreateCornerSimFiles_ Output:
# Creates corner_sim.sh and corner_0, corner_1 ... corner_n folder
#
# Each corner folder will have respective corner simulation file
# Header of the corner simulation file will specify the corner information
# 
# After running this script, run "source corner_sim.sh". This will create 
# raw files in the respective corner folder
# =============================================================================
model_file='/home/nataraj/projects/designmyic/cad/pdk/share/pdk/sky130B/libs.tech/ngspice/sky130.lib.spice'
sim_dir = '/home/nataraj/projects/designmyic/cad/cygnus/examples/rc'
tb= 'tb_rc.spice'
corners={'lib':['ff','ss'],'RLOAD':[1e3,1e4]}

_CreateCornerSimFiles_(sim_dir,tb, model_file, corners)
                      