from cygnus.cygnus import *
def ReportSpiceOutputs(sim_dir,check_outputs,check_expr,corner_id, show_plots):
    
    
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
            arrs, plots = RawRead(rawfile)
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
            arrs, plots = RawRead(rawfile)
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