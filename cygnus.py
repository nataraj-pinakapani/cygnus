# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import os
import itertools
import matplotlib.pyplot as plt
import subprocess

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
    
    # =============================================================================
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
    # =============================================================================
    
    if rawfile_path==0:
        rawfile_path=os.getenv('HOME')+'/.xschem/simulations/'
    file=rawfile_path+rawfile
    arrs, plots = rawread(file)
    arrs=np.array(arrs)    
    noise_dict={}
    noise_keys=[]
    noise_values=[]
    noise_devices=[]
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
        
def _CreateCornerSimFiles_(sim_dir, tb, model_file, corners,run=0):
    #print(tb)
    #print(spicelib)
    
    corners_json={}
    if(corners=={}):
        print("Sim Corners Not given")
        return
    else:
        keys=[]
        values=[]
        for key, value in corners.items():
            keys.append(key)
            values.append(value)  
               
        # using itertools.product()  
        # to compute all possible permutations
        sim_corners = list(itertools.product(*values))
          
        # printing result
        i=0
        
        for corner in sim_corners:
            temp_json= dict(zip(keys,corner))
            corners_json[i]=temp_json
            i+=1
        
        #print(corners_json)
        
        cmd="rm -rf "+sim_dir+'/corner*'
        os.system(cmd)
        
        file=sim_dir+'/corner_legend.txt'
        lines=[]
        for corner in corners_json.keys():
            lines.append(str(corner)+ " corners_"+str(corner)+' '+str(corners_json[corner])+'\n')
        with open(file, 'w') as f:
            for line in lines:
                f.write(line)
            f.close()
            
        corner_dirs=[]
        for i in range(len(corners_json)):
            
            #print(corners_json[i+1])
            corner_dir=sim_dir+'/corner_'+str(i)
            cmd='mkdir '+corner_dir
            os.system(cmd)
            corner_dirs.append(corner_dir)
            lines=[]
            lines.append("* Netlist: "+ tb)
            lines.append("* Corner: "+ str(corners_json[i]))

            lines.append('\n.control')
            for key in corners_json[i].keys():  
                if not key =='lib':
                    lines.append('\nalter '+key+' '+str(corners_json[i][key]))
            lines.append('\n.endc')    
            
            lines.append('\n.lib '+model_file+' '+ corners_json[i]['lib'])
            lines.append('\n.include '+sim_dir+'/'+tb)     
            
            
            file=corner_dir+'/corner_'+str(i)+'.sp'
            with open(file, 'w') as f:
                for line in lines:
                    f.write(line)
                f.close()
            file=sim_dir+'/corners_sim.sh'
            lines=[]
            with open(file, 'w') as f:
                line='#!/bin/bash\n'
                f.write(line)
                for i in range(len(corner_dirs)):
                    line="cd "+corner_dirs[i]+'\nngspice -b '+ corner_dirs[i]+'/corner_'+str(i)+'.sp\n'
                    f.write(line)
                line='cd '+sim_dir
                f.write(line)
                f.close()
        #print(len(corners_json))
        if(run==0):
            print("Run source ",file, "to run the corner sims")
            return
        elif(run==1):

            os.system('/bin/bash -c source HOME/.bashrc')
            cmd=subprocess.call(["/bin/sh", file])
            print(cmd)
            os.system(cmd)
            print("Please check corner sim resilts in corner_<#> folders")
            
"""
_CreateCornerSimFiles_(sim_dir='/home/nataraj/projects/designmyic/cad/cygnus/examples/rc',\
                       tb='tb_rc.spice',\
                       model_file='/home/nataraj/projects/designmyic/cad/pdk/share/pdk/sky130B/libs.tech/ngspice/sky130.lib.spice',\
                       corners={'lib':['ff','ss'],'RLOAD':[1e2, 1e4]}, run=0)
"""
            
def _RunCornerSim_(cornerfile):
    cmd='source '+cornerfile
    print(cmd)
    os.system(cmd)

#_RunCornerSim_('corner.sp')


def _ReportSpiceOutputs_(sim_dir,check_outputs,check_expr,corner_id={'from':0, 'to':1}):
    
    print("This script will check if "+check_expr+" in "+check_outputs['sim_name']+\
          " simulation is within "+ str(check_outputs['range'][0])+" and "+str(check_outputs['range'][1]))
    print('---------------------------------------------------------------------------------------------',end='\n\n')
    print('Please find simulation/testbench settings for the corners in '+sim_dir+'/corners_legend.txt',end='\n\n')
    corner_ids=[]
    corner_dirs=[]
    corner_results={'sim_name':check_outputs['sim_name']}
    i=corner_id['from']
    while i<=corner_id['to']:
        corner_result={}
        corner_ids.append(i)
        corner_dirs.append('corner_'+str(i))
        rawfile=sim_dir+'/corner_'+str(i)+'/'+check_outputs['sim_name']+'.raw'
        arrs, plots = rawread(rawfile)
        arrs=np.array(arrs)
        for vector in check_outputs['vectors'].values():
            corner_result[vector]=arrs[vector][0]
        corner_result[check_expr]=corner_result['v(in)']-corner_result['v(out)']
        if not (check_outputs['range'][0]<=corner_result[check_expr]<=check_outputs['range'][1]):
            print("Error in Corner_"+str(i)+"-->"+check_expr+" = "+str(round(corner_result[check_expr][0],3)))
        corner_results[i]=corner_result
        
        i+=1
        
    i=corner_id['from']
    final_result=[]
    min_val=1e100
    max_val=0
    while i<=corner_id['to']:
        final_result.append(corner_results[i][check_expr])
        if (corner_results[i][check_expr]>max_val):
            max_val=corner_results[i][check_expr][0]
            max_corner=i
        if (corner_results[i][check_expr]<min_val):
            min_val=corner_results[i][check_expr][0]
            min_corner=i
        i+=1
        
        
    print("Max. "+ check_expr +" = "+ str(round(max_val,3))+" in corner_"+str(max_corner))
    print("Min. "+ check_expr +" = "+ str(round(min_val,3))+" in corner_"+str(min_corner))
    plt.scatter(corner_ids, final_result)
    plt.plot(corner_ids, final_result)
    plt.xlabel('corner_id')
    plt.ylabel(check_expr)
    plt.title(check_expr+" Vs Corners Plot")
    plt.show()
        
    
    #print(corner_results)
    
        #print(name)
        #noise_dict[name]=[round(arrs[name][0][0]*1e6,2),round(100*arrs[name][0][0]/arrs['v(inoise_total)'][0][0],2)]

vectors={'a':'v(out)', 'b':'v(in)'}

_ReportSpiceOutputs_(sim_dir='/home/nataraj/projects/designmyic/cad/cygnus/examples/rc', \
                      check_outputs={'sim_name':'op', 'vectors':vectors, 'range':[1,2]},\
                      check_expr="v(out)-v(in)",\
                      corner_id={'from':0, 'to':3})
