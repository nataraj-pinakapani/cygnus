# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import os



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
def _CreateCornerSimFiles_(tb, spicelib, sim_dir,process_corners,sim_cmds,sweep_params=0):
    print(tb)
    print(spicelib)
    print(process_corners)
    corners=len(process_corners)
    cornerfiles=[]
    i=0
    for proc in process_corners:
        cornerfiles.append(sim_dir+'/corner_'+proc+'.sp')
        file=sim_dir+'/corner_'+proc+'.sp'
        with open(file, 'w') as f:
            line='.include '+tb
            f.write(line)
            line='\n.lib /home/nataraj/projects/designmyic/cad/pdk/share/pdk/sky130B/libs.tech/ngspice/sky130.lib.spice '+proc
            f.write(line)
            
            i=0
            for cmd in sim_cmds:
                line='\n.control\n'+cmd+'\n\nwrite '+proc+str(i)+'.raw\n.endc'
                f.write(line)
                i+=1
        f.close()
    
spicelib='/home/nataraj/projects/designmyic/cad/pdk/share/pdk/sky130B/libs.tech/ngspice/sky130.lib.spice'
cornerfile_path='/home/nataraj/projects/designmyic/cad/cygnus/examples/res_div'
_CreateCornerSimFiles_(tb='tb_res_div.spice',\
                       spicelib=spicelib,\
                       sim_dir='/home/nataraj/projects/designmyic/cad/cygnus/examples/res_div',\
                       process_corners=['tt', 'ff', 'ss'],\
                       sim_cmds=['dc temp 0 100 1 VIN 0 3 0.5'])


def _RunCornerSim_(cornerfile):
    cornerfile_path='/home/nataraj/projects/designmyic/cad/cygnus/examples/res_div'
    cmd='ngspice -b '+ cornerfile_path+'/'+cornerfile
    print(cmd)
    os.system(cmd)

#_RunCornerSim_('corner.sp')