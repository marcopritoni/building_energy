import MV_model
from IPython.display import Image

# Main
if __name__ == "__main__":
   
    # file source variables
    FOLDER='data'
    FILE= 'Ghausi_M&V Data.csv'
    #FILE= 'PES_M&V Data.csv'
    
# LOAD DATA
    dwnld_data=get_data(os.path.join(FOLDER,FILE))

# CLEAN DATA
    data=add_variables(dwnld_data)   
    data=clean_data(data)
    #print data

## TASKS
    explor=False #plots exploratory graphs
    search=True # iterates to get best model
    
# define pre-post    
    pre_start =pd.to_datetime('4,1,2016',  format='%m,%d,%Y', errors ='coerce', dayfirst=False)
    pre_end = pd.to_datetime('11,1,2016', format='%m,%d,%Y', errors ='coerce', dayfirst=False)
    post_start =pd.to_datetime('11,1,2016', format='%m,%d,%Y', errors ='coerce', dayfirst=False)
    post_end = pd.to_datetime('11,1,2017', format='%m,%d,%Y', errors ='coerce', dayfirst=False)
    data["PrePost"]=np.nan
    data.loc[pre_start:pre_end,"PrePost"]=0
    data.loc[post_start:post_end,"PrePost"]=1

# select energy type variables
    energy_type=["chw","elec", "steam"]
    #energy_type=["chw"]
# select other regressors
    var = ['hdh','cdh']
# select regression algorithm    
    algorithm =2
    mod_type =2
    
### PLOTS FOR EACH ENERGY TYPE
# PLOT GROUP 1: DATA EXPLORATORY GRAPHS
    if explor==True:
        for tar in energy_type:
# PLOT G1-1: profile of energy by hour of day, a line per month       
            #plot_energy_profile_byMo("2012", "2013", data, tar)
        
# PLOT G1-2: WD/WE profiles in time 
# note: add holidays !!!! 
            #plot_WD_WE (data, tar) 

# PLOT G1-3: scatter plot
            x_var="oat"
            perPre=0
            perPost=1
            plot_scatter (data, tar, x_var, perPre, perPost)
        
    print "data time range:  %s - %s \n" % (data.index.min(), data.index.max())

### FOR LOOP 1: cycle through energy types    
    score_tot={}
    saving_cost={}
    saving_perc={}
    uncert_tot={}
    
    
    for tar in energy_type: # as an alternative to define it explicitely use k-fold cross validation with sci-kit learn...

# Training Period - Use the full period, then the validation will be dropped later
        train_start =pre_start
        train_end = pre_end
# Validation Period; va
        val_start =pd.to_datetime('4,1,2015',  format='%m,%d,%Y', errors ='coerce', dayfirst=False)
        val_end = pd.to_datetime('4,7,2015',  format='%m,%d,%Y', errors ='coerce', dayfirst=False)

# period to calculate savings over
        pred_start = post_start
        pred_end = post_end
        
        data.loc[train_start:train_end,"Period"]=1
        data.loc[val_start:val_end,"Period"]=2
        data.loc[pred_start:pred_end,"Period"]=3
               
        print "Target Var is        %s" % (tar)
        print "Training time range:   %s - %s" % (train_start, train_end)
        print "Validation time range: %s - %s" % (val_start, val_end)
        
# TRAIN MODEL        
        ret_obj=train_model (data, tar, var, algorithm, mod_type, train_start, train_end, val_start, val_end)
    
# save results
        curr_model=ret_obj["model"]
        model_col=ret_obj["model_col"]
        model_data=ret_obj["model_data"]
        score_train=ret_obj["score"]
        target_modeled_train=ret_obj["target_modeled_train"]
        compare_train=ret_obj["compare"]
        #temp=ret_obj["data_train"]

#save scores
        score_tot[tar]={}
        score_tot[tar]["score_train"]=calc_scores(compare_train,len(model_col)) 
        print "score train = "
        print score_tot[tar]["score_train"]
        
# PREDICT AND COMPARE
        ret_obj2=predict_model(model_data, tar, model_col, curr_model, val_start, val_end)   

    # save results
        score_val=ret_obj2["score"]
        target_modeled_val=ret_obj2["target_modeled_val"]
        compare_val=ret_obj2["compare"]
    
        score_tot[tar]["score_val"]=calc_scores(compare_val,len(model_col)) 
        print "score val = "
        print score_tot[tar]["score_val"]
        print "\n"
        score_table=pd.Panel(score_tot).transpose(1,0,2).to_frame() #build score table
        
# CALCULATE SAVINGS
        ret_obj3=calc_savings(model_data, tar, model_col, curr_model, pred_start, pred_end) 
        compare_sav=ret_obj3["compare"]
        
        ret_obj4=savings_table_byMo(compare_sav, tar, cost)
        saving_cost.update(ret_obj4["data_cost_sav"])
        saving_perc.update(ret_obj4["data_perc_sav"])
        
# UNCERTAINTY        
        #uncert_tot.update(calc_uncert)
        print calc_uncert(compare_train, compare_sav, 95, score_tot, tar, absol=True)
# PLOT MODEL
        plot_compare(compare_train,compare_train.index.min(),compare_train.index.max())
        plot_compare(compare_val,compare_val.index.min(),compare_val.index.max())
        plot_compare(compare_sav,compare_sav.index.min(), compare_sav.index.max())
# PLOT SAVINGS        
        plot_PrePost_byMo(data, tar)
        plot_ModPost_byMo(compare_sav, tar)
        plot_PrePostSav_byMo(data, tar)
        plot_ModPostSav_byMo(compare_sav, tar)

    saving_cost=pd.DataFrame(saving_cost).T
    saving_perc=pd.DataFrame(saving_perc).T

    print score_table
    print saving_cost
    print saving_perc
    print saving_cost.sum()[2:].sum()
    print saving_perc.sum()[2:].sum()
