#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 10:40:09 2022

@author: nataraj
"""

from cygnus import _ReportSpiceOutputs_

#https://www.pythonforthelab.com/blog/how-create-setup-file-your-project/

# =============================================================================
# _ReportSpiceOutputs_ Purpose:
# ------------------------------
# The script will report if the simulated value of the expression specified by 
# "check_expr" is within the range specified by check_outputs['range']

# If check_expr falls out of range, the script will report the error with the 
# corner information. The details of the corners can be found in 
# sim_dir/corner_legend.txt

# The script will also report the max. and min. values of check_expr

# Finally, the script will plot the graph of "corner_id" Vs "check_expr"

# _ReportSpiceOutputs_ Usage:
# ------------------------------
# Specify the following variables and run the script

# sim_dir --> Full path of Sim Dir. Must have testbench file

# vectors={'a':'v(out)', 'b':'v(in)'} --> Note the keys a & b

# check_outputs --> {{'sim_name':'op', 'vectors':vectors, 'range':[0,0.5]}}

# corners Eg: corners={'lib':['ff','ss'],'RLOAD':[1e3,1e4]}

# check_expr="b-a" --> v(out)-v(in) is represented as b-a, based on the keys of
# v(out) and v(in) in vectors respectively

# corner_id={'from':0, 'to':3} --> sim_dir/corner_legend.txt contains the 
# corner details
# =============================================================================
sim_dir = '/home/nataraj/projects/designmyic/cad/cygnus/examples/rc'
vectors={'a':'v(out)', 'b':'v(in)'}
check_outputs={'sim_name':'op', 'vectors':vectors, 'range':[0,0.5]}
check_expr="b-a"              
corner_id={'from':0, 'to':3}        


_ReportSpiceOutputs_(sim_dir,check_outputs,check_expr,corner_id)