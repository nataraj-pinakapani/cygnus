# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import os

BSIZE_SP = 512 # Max size of a line of data; we don't want to read the
               # whole file to find a line, in case file does not have
               # expected structure.
MDATA_LIST = [b'title', b'date', b'plotname', b'flags', b'no. variables',
              b'no. points', b'dimensions', b'command', b'option']

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
    if rawfile_path==0:
        rawfile_path=os.getenv('HOME')+'/.xschem/simulations/'
    file=rawfile_path+rawfile
    arrs, plots = rawread(file)
    arrs=np.array(arrs)
    #print("VD=",arrs0['v(d)'])
    #print("VG=",arrs0['v(g)'])
    #print("ID=",arrs0['i(vds)']*-1)
    #plt.scatter(arrs0['v(g)'][0],arrs0['i(vds)'][0]*-1, color='black')
    
    #plt.scatter(l0.get_data('v(g)'),l0.get_data('i(vds)')*-1, color='black')
    #plt.scatter(l1.get_data('v(g)'),l1.get_data('i(vds)')*-1, color='red')
    #plt.show()
    #plt.scatter(l2.get_data('v(g)'),l2.get_data('i(vds)')*-1, color='green')
    #plt.scatter(arrs1['v(g)'][0],arrs1['i(vds)'][0]*-1, color='blue')
    #plt.show()
    
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
                   
    
    #for i in range(len(noise_contributors)):
    #    print(noise_contributors[i])
    
    #print(len(arrs.dtype))
    #for i in range(len(arrs.dtype)):
    #    print(arrs.dtype[i].names)

_FindNoiseContributors_(rawfile='ldo_2_noise.raw', num_of_contributors=30)
