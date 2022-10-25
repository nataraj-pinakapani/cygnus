# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import os
import itertools
import matplotlib.pyplot as plt
import subprocess
import cexprtk

def rawread(fname: str):
    """Read ngspice binary raw files. Return tuple of the data, and the
    plot metadata. The dtype of the data contains field names. This is
    not very robust yet, and only supports ngspice.
    >>> darr, mdata = rawread('test.py')
    >>> darr.dtype.names
    >>> plot(np.real(darr['frequency']), np.abs(darr['v(out)']))
    """
    # Example header of raw file
    # Title: rc band pass example circuit
    # Date: Sun Feb 21 11:29:14  2016
    # Plotname: AC Analysis
    # Flags: complex
    # No. Variables: 3
    # No. Points: 41
    # Variables:
    #         0       frequency       frequency       grid=3
    #         1       v(out)  voltage
    #         2       v(in)   voltage
    # Binary:
        
    BSIZE_SP = 512 # Max size of a line of data; we don't want to read the
                   # whole file to find a line, in case file does not have
                   # expected structure.
    MDATA_LIST = [b'title', b'date', b'plotname', b'flags', b'no. variables',
                  b'no. points', b'dimensions', b'command', b'option']
    
    fp = open(fname, 'rb')
    plot = {}
    count = 0
    arrs = []
    plots = []
    while (True):
        try:
            mdata = fp.readline(BSIZE_SP).split(b':', maxsplit=1)
        except:
            raise
        if len(mdata) == 2:
            if mdata[0].lower() in MDATA_LIST:
                plot[mdata[0].lower()] = mdata[1].strip()
            if mdata[0].lower() == b'variables':
                nvars = int(plot[b'no. variables'])
                npoints = int(plot[b'no. points'])
                plot['varnames'] = []
                plot['varunits'] = []
                for varn in range(nvars):
                    varspec = (fp.readline(BSIZE_SP).strip()
                               .decode('ascii').split())
                    assert(varn == int(varspec[0]))
                    plot['varnames'].append(varspec[1])
                    plot['varunits'].append(varspec[2])
            if mdata[0].lower() == b'binary':
                rowdtype = np.dtype({'names': plot['varnames'],
                                     'formats': [np.complex_ if b'complex'
                                                 in plot[b'flags']
                                                 else np.float_]*nvars})
                # We should have all the metadata by now
                arrs.append(np.fromfile(fp, dtype=rowdtype, count=npoints))
                plots.append(plot)
                fp.readline() # Read to the end of line
        else:
            break
    return (arrs, plots)


def _FindNoiseContributors_(rawfile,num_of_contributors,rawfile_path=0):
    
    # =========================================================================
    # _FindNoiseContributors_ Usage:
    # ------------------------------
    # _FindNoiseContributors_ (<str:rawfile_name>, <integer:num_of_contributors>,\
    #   [<str:rawfile path>])
    # rawfilepath is optional. If not specified, the script will search for file in
    # /$HOME/.xschem/simulations/
    # 
    # To create a raw binary file from noise simulation, add the following commands
    # in the .control block in ngspice netlist before running the simulation
    #
    # noise v(vout) V6 dec 10 1kHz 100MEG 1 *<== must add 1 after 100MEG
    # setplot noise2
    # write ldo_2_noise2.raw
    #
    # 
    # =========================================================================
    
    if rawfile_path==0:
        rawfile_path=os.getenv('HOME')+'/.xschem/simulations/'
    file=rawfile_path+rawfile
    arrs, plots = rawread(file)
    arrs=np.array(arrs)    
    noise_dict={}
    noise_keys=[]
    i=0
    
    for name in arrs.dtype.names:
        if('inoise' in name):
            noise_keys.append(name)
            noise_dict[name]=[round(arrs[name][0][0]*1e6,2),round(100*arrs[name][0][0]/arrs['v(inoise_total)'][0][0],2)]

# =============================================================================
# Comment1:
# Added to remove redundant noise information that reports noise contribution 
# from individual segmets
# =============================================================================
    """
    for key in noise_keys:
        temp=key.removeprefix('v(inoise_total.')
        temp1=temp.removesuffix(')')
        noise_devices.append(temp1)
    print(noise_devices)
    """
# =============================================================================
# Comment1: Ends       
# =============================================================================            
            

    noise_sorted=sorted(noise_dict.items(), key=lambda x:x[1], reverse=True)
    num = min(num_of_contributors+1,len(noise_sorted) )
    print("Top", num-1, "noise contributors")
    print("Format:")
    print("No.: (Noise Contributor, [Total Integrated Noise in uV, Percentage Contribution])")
    print('--------------------------------------------------------------------------------')
    for i in range(num):
        print(i, ": ",noise_sorted[i])
# =============================================================================
# =============================================================================
        
def _ReportSpiceOutputs_(sim_dir,check_outputs,check_expr,corner_id, show_plots):
    
    
    corner_ids=[]
    corner_dirs=[]
    corner_results={'sim_name':check_outputs['sim_name']}
    i=corner_id['from']
    for vector_key, vector in check_outputs['vectors'].items():
        print(vector_key,'=',vector)
    print(end='\n\n')
    
    if(check_outputs['sim_type']=='op'):
        print("This script will check if "+check_expr+" in "+check_outputs['sim_name']+\
              " simulation is within "+ str(check_outputs['range'][0])+" and "+str(check_outputs['range'][1]))
        print('---------------------------------------------------------------------------------------------',end='\n\n')
        print('Please find simulation/testbench settings for the corners in '+sim_dir+'/corners_legend.txt',end='\n\n')
        while i<=corner_id['to']:
            corner_result={}
            corner_ids.append(i)
            corner_dirs.append('corner_'+str(i))
            rawfile=sim_dir+'/corner_'+str(i)+'/'+check_outputs['sim_name']+'.raw'
            arrs, plots = rawread(rawfile)
            arrs=np.array(arrs)
            eval_expr_input={}
            for vector_key, vector in check_outputs['vectors'].items():
                corner_result[vector]=arrs[vector][0]
                eval_expr_input[vector_key]=corner_result[vector][0]
                
            corner_result[check_expr]=cexprtk.evaluate_expression(check_expr, eval_expr_input)
            
            if not (check_outputs['range'][0]<=corner_result[check_expr]<=check_outputs['range'][1]):
                print("Error in Corner_"+str(i)+"-->"+check_expr+" = "+str(round(corner_result[check_expr],3)))
            corner_results[i]=corner_result
            
            i+=1
            
        i=corner_id['from']
        final_result=[]
        min_val=1e100
        max_val=-1e100
        while i<=corner_id['to']:
            final_result.append(corner_results[i][check_expr])
            if (corner_results[i][check_expr]>max_val):
                max_val=corner_results[i][check_expr]
                max_corner=i
            if (corner_results[i][check_expr]<min_val):
                min_val=corner_results[i][check_expr]
                min_corner=i
            i+=1     
            
        print("Max. "+ check_expr +" = "+ str(round(max_val,3))+" in corner_"+str(max_corner))
        print("Min. "+ check_expr +" = "+ str(round(min_val,3))+" in corner_"+str(min_corner))
        plt.scatter(corner_ids, final_result)
        plt.plot(corner_ids, final_result)
        plt.xlabel('corner_id')
        plt.ylabel(check_expr)
        plt.title('Corners Vs '+check_expr+ ' Plot')
        plt.show()
    
    
    elif(check_outputs['sim_type']=='dc'):
        i=corner_id['from']
        corner_result={}
        while i<=corner_id['to']:
            corner_result[i]={}
            corner_ids.append(i)
            corner_dirs.append('corner_'+str(i))
            rawfile=sim_dir+'/corner_'+str(i)+'/'+check_outputs['sim_name']+'.raw'
            arrs, plots = rawread(rawfile)
            arrs=np.array(arrs)
            for vector_key, vector in check_outputs['vectors'].items():
                corner_result[i][vector]=arrs[vector]      
                
            i+=1
    
    
        i=corner_id['from']
        while i<=corner_id['to']:
            for plot in show_plots:
                x=corner_result[i][plot[0]]
                y=corner_result[i][plot[1]]
                plt.scatter(x,y)
                plt.plot(x,y)
                plt.show()
            
            i+=1

    return    
# =============================================================================
# =============================================================================   
