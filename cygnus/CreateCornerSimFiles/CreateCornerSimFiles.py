from cygnus.cygnus import *
def CreateCornerSimFiles(sim_dir, tb, model_file, corners,run=0):
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
            lines.append(str(corner)+' '+str(corners_json[corner])+'\n')
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