from cygnus.cygnus import *
def FindNoiseContributors(rawfile,num_of_contributors,rawfile_path=0):
    
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
    arrs, plots = RawRead(file)
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
