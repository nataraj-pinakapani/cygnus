#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 10:40:09 2022

@author: nataraj
"""

from cygnus import _ReportSpiceOutputs_
#https://www.pythonforthelab.com/blog/how-create-setup-file-your-project/

# =============================================================================
# Comment1:
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
sim_dir = '/home/nataraj/projects/designmyic/cad/cygnus/examples/rc'
vectors={'a':'v(out)', 'b':'v(in)'}
                       
_ReportSpiceOutputs_(sim_dir='/home/nataraj/projects/designmyic/cad/cygnus/examples/rc', \
                      check_outputs={'sim_name':'op', 'vectors':vectors, 'range':[0,0.5]},\
                      check_expr="v(out)",\
                      corner_id={'from':0, 'to':3})