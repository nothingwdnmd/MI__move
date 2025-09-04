# -*- coding: utf-8 -*-

import numpy as np
    
from bandpassx import BANDPASSx as bandpassx
from calcspx import CALCSPx as calcspx
# from plotsome import PLOTSOMEx as plotsomex


from mne.io import concatenate_raws, read_raw_edf
import mne
import os
import debugPrinter as dp
# import matplotlib.pyplot as plt
import json
import pickle

# from sklearn.metrics import 
import pandas as pd
# import pymrmr

# import pandas as pd
from sklearn import feature_selection
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV

def calculate_model():    
    
    # plt.close('all')
    
    # 6 filters (i.e., 3 pairs), corresponding to the 3 largest and 3 lowest of csp
    csp_feature_index = np.array([0,1,2,-3,-2,-1])
    # csp_feature_index = np.array([0,1,-2,-1])
    
    # pairs of CSP features selected in mutual info
    k=6
    
    trianingDataFolder = './training_data/'
    
    with open('task_markers.json', 'r') as file:
        markers = json.load(file)
        
    
    label_left_int = markers['left'][0]
    label_right_int = markers['right'][0]
    
    file_list=[]
    for file_name in os.listdir(trianingDataFolder):
        file_list.append(trianingDataFolder+file_name)
    
    raw_list = []
    evt_list=[]
    evt_dic_list = []
    for f in file_list:
        raw_tmp = read_raw_edf(f,preload=False)
        raw_list.append(raw_tmp)
        events_from_annot,event_dict = mne.events_from_annotations(raw_tmp)
        evt_list.append(events_from_annot)
        evt_dic_list.append(event_dict)
        
    
    raw_=concatenate_raws(raw_list,events_list=evt_list)
    raw = raw_[0]
    evt = raw_[1]
    
    fs = raw.info['sfreq']
    nchannels, nsamples = raw.get_data().shape      
    
    key_list = list(event_dict.keys())
    val_list = list(event_dict.values())
    
    events_marker = evt.copy()
    
    for i, c in enumerate(evt[:,2]):
        tmp = key_list[val_list.index(c)]
        tmp = int(float(tmp))
        events_marker[i,2]=tmp
    
    events_marker = np.delete(events_marker,np.where((events_marker[:,2]!=label_left_int) & (events_marker[:,2]!=label_right_int))[0],0)
    
    cl_lab = ['left','right']
    
    evnet_dict_marker = {
        'left':label_left_int,
        'right':label_right_int    
    }
    
    # fig = mne.viz.plot_events(
    #     events_marker, event_id=evnet_dict_marker, sfreq=raw.info["sfreq"], first_samp=raw.first_samp
    # )
    
    signal_win_start = 0.5 #second
    signal_win_end = 2.5 #second
    
    epochs = mne.Epochs(
        raw,
        events_marker,
        event_id=evnet_dict_marker,
        tmin=signal_win_start,
        tmax=signal_win_end,
        baseline = None
    )
    
    trial_num={}
    for cl in cl_lab:
        trial_num[cl] = sum(events_marker[:,2]==evnet_dict_marker[cl])
    
    trials_raw={}
    trials_max_value = {}
    for cl in cl_lab:
        tmp = epochs[cl].get_data()
        trials_raw[cl] = tmp.transpose((1, 2, 0)).copy()
        tmp2 = tmp.reshape(tmp.shape[0],-1)
        trials_max_value[cl] = np.max(tmp2,axis=1)
    
    # # deleted bad trials
    bad_trial_thr = 0.00015
    
    bad_trials_idx = {}
    for cl in cl_lab:
        bad_trials_idx[cl]=trials_max_value[cl]>bad_trial_thr
        trials_raw[cl] = np.delete(trials_raw[cl],bad_trials_idx[cl], axis=2)
    
    # check the max value of the trials
    # plt.figure()
    # plt.plot(trials_max_value['left'],color='blue')
    # plt.plot(trials_max_value['right'],color='green')
    # plt.plot([0,trial_num['left']],[bad_trial_thr,bad_trial_thr],':')
    
    for cl in cl_lab:
        trial_num[cl] = trial_num[cl]-sum(bad_trials_idx[cl])
    
    
    # # check the bad trials have been deleted
    # for cl in cl_lab:
    #     tmp = trials_raw[cl]
    #     d = tmp.shape[2]
    #     tmp2 = tmp.transpose((2, 0, 1)).reshape(d,-1)
    #     trials_max_value[cl] = np.max(tmp2,axis=1)
        
    # plt.figure()
    # plt.plot(trials_max_value['left'],color='blue')
    # plt.plot(trials_max_value['right'],color='green')
    # plt.plot([0,trial_num['left']],[bad_trial_thr,bad_trial_thr],':')
    
    # # check some trials
    # plt.figure()
    # plt.plot(trials_raw['left'][0,:,49])
    
    # filter bank:
    # 1. 4-8Hz
    # 2. 8-12Hz
    # 3. 12-16Hz
    # 4. 16-20Hz
    # 5. 20-24Hz
    # 6. 24-28Hz
    # 7. 28-32Hz
    band_interval = 4
    filter_band = np.arange(4, 32, step = int(band_interval/2))
    # filter_band = np.arange(4, 32, step = band_interval)
    filter_bands_str_num={}
    
    for band_lo in filter_band:
        # This will be new key inside the EEG_filtered
        lo = band_lo
        hi = band_lo+band_interval
        band = "{:02d}_{:02d}".format(lo,hi)    
        print(': {} Hz'.format(band))
        filter_bands_str_num[band]=[lo,hi]
    
    
    trials_all = {}    
    for band_str, band_list in filter_bands_str_num.items(): 
        print('Filtering through '+band_str+' Hz band')
        lo, hi = band_list    
        mbandpassx48 = bandpassx(fs, lo, hi)
        tmp = {}
        for cl in cl_lab:
            tmp[cl] = mbandpassx48.apply_filter(trials_raw[cl])
            
        trials_all[band_str] = tmp
    
    #%%
    
    
    mW_all_bands = {}
    X = np.array([]).reshape(trial_num['left']+trial_num['right'],0)
    mcspx = calcspx()
    
    for band_key, trials in trials_all.items():         
    
         mW = mcspx.get_csp_w(trials['left'], trials['right'])
         mW_all_bands[band_key] = mW
         trials_csp_cl1 = mcspx.apply_csp(mW, trials['left'])
         trials_csp_cl2 = mcspx.apply_csp(mW, trials['right'])
         trials_csp = {'left': trials_csp_cl1,'right': trials_csp_cl2}
    
         # plot the figures
         # nsamples_win = len(np.arange(int(signal_win_start*fs), int(signal_win_end*fs)))
         # mplt = plotsomex(nchannels, nsamples_win, fs)    
         # mplt.plot_psd_simple(trials_csp['left'],trials_csp['right'])
    
         trials_csp_f={}
         trials_csp_f['left'] = trials_csp['left'][csp_feature_index,:,:]
         trials_csp_f['right'] = trials_csp['right'][csp_feature_index,:,:]
        
         trials_logvar = {'left': np.log(np.var((trials_csp_f['left']), axis=1)),
                          'right': np.log(np.var((trials_csp_f['right']), axis=1))}
    
         x = np.concatenate((trials_logvar['left'].T,trials_logvar['right'].T),axis = 0)
         X = np.concatenate((X,x),axis = 1)                 
    
    
    y = np.concatenate((np.ones((trial_num['left']))*evnet_dict_marker['left'],np.ones((trial_num['right']))*evnet_dict_marker['right']),axis = 0)
    
    # use mutual infomation rank
    mutual_info = feature_selection.mutual_info_classif(X,y)
    mutual_info_rank = np.argsort(mutual_info)[::-1]
    mutual_info_rank_use = mutual_info_rank[:k];
    
    # # use mrmr
    # yy = np.expand_dims(y, axis=1)
    # ar_xy = np.concatenate((yy,X),axis = 1)
    # name_list = [str(x) for x in range(X.shape[1])] 
    # name_list.insert(0,'class')
    # df_data = pd.DataFrame(ar_xy,columns = name_list)
    # sel_features_idx_str = pymrmr.mRMR(df_data, 'MID', k)
    # sel_features_idx = np.array([int(x) for x in sel_features_idx_str])
    # mutual_info_rank_use = sel_features_idx
    
    X_train_mutual_info = X[:,mutual_info_rank_use]    
    
    # clf = make_pipeline(StandardScaler(), SVC(gamma='auto'))
    # clf.fit(X_train, y)
    # Pipeline(steps=[('standardscaler', StandardScaler()),
    #                 ('svc', SVC(gamma='auto'))])

    std = StandardScaler()
    X_train_mutual_info_std = std.fit_transform(X_train_mutual_info)
    
    params = {
        'C':[0.1, 1, 10, 100, 1000],
        'gamma':['scale',1,0.1,0.001,0.001,0.0001],
        'kernel':['rbf','linear', 'poly','sigmoid']
        }
    
    # optimal_params = GridSearchCV(SVC(), param_grid=params, cv=5)
    optimal_params = GridSearchCV(SVC(),param_grid=params,cv=5)
    
    optimal_params.fit(X_train_mutual_info_std, y)
    
    # print('best paras: ',optimal_params.best_estimator_)
    # print('best score: ',optimal_params.best_score_)
    
    clf = SVC(C=optimal_params.best_params_['C'],
              gamma=optimal_params.best_params_['gamma'],
              kernel=optimal_params.best_params_['kernel'],
              random_state=42)
    clf.fit(X_train_mutual_info_std,y)
 
    train_model = {}
    train_model['clf'] = clf
    train_model['csp'] = mW_all_bands
    train_model['mu_inf'] = mutual_info_rank_use
    train_model['filter_bands'] = filter_bands_str_num
    train_model['fs'] = fs
    train_model['signal_win_start'] = signal_win_start
    train_model['signal_win_end'] = signal_win_end
    train_model['csp_feature_index'] = csp_feature_index
    train_model['std'] = std

    filePathName = './models/new_model_bv8#p!_.mim'
    if os.path.isfile(filePathName):
        os.remove(filePathName)    
        
    pickle.dump(train_model,open(filePathName,'wb'))    
    
    dp.dpt('----------------------')
    
    #%% check the data by seperate it into training set and test set
    # if_check = 1
    # if if_check!=1:
    #     return
    
    percentage_train_test = 0.7
    
    
    trial_num_train = {}
    trial_num_test = {}
    for cl in cl_lab:   
        trial_num_train[cl]=round(trial_num[cl]*percentage_train_test)
        trial_num_test[cl]=trial_num[cl]-trial_num_train[cl]
        # trial_numt= np.sum(event_codes == code)
    
    
    X = np.array([]).reshape((trial_num_train['left']+trial_num_train['right']),0)
    mW_all_bands = {}
    
    for band_key, trials in trials_all.items():         
    
        trials_train={}
        for cl in cl_lab:   
          trials_train[cl] = trials[cl][:,:,:trial_num_train[cl]]
         
        mW = []
        trials_csp={}
        mW = mcspx.get_csp_w(trials_train['left'], trials_train['right'])
        trials_csp_cl1 = mcspx.apply_csp(mW, trials_train['left'])
        trials_csp_cl2 = mcspx.apply_csp(mW, trials_train['right'])
        trials_csp = {'left': trials_csp_cl1,'right': trials_csp_cl2}
        mW_all_bands[band_key] = mW
    
        # plot the figures
        # nsamples_win = len(np.arange(int(signal_win_start*fs), int(signal_win_end*fs)))
        # mplt = plotsomex(nchannels, nsamples_win, fs)    
        # mplt.plot_psd_simple(trials_csp[cl1],trials_csp['right'])
    
        trials_csp_f={}
        trials_csp_f['left'] = trials_csp['left'][csp_feature_index,:,:]
        trials_csp_f['right'] = trials_csp['right'][csp_feature_index,:,:]
    
        trials_logvar = {'left': np.log(np.var((trials_csp_f['left']), axis=1)),
                      'right': np.log(np.var((trials_csp_f['right']), axis=1))}
    
        x = np.concatenate((trials_logvar['left'].T,trials_logvar['right'].T),axis = 0)
        X = np.concatenate((X,x),axis = 1)     
    
    y = np.concatenate((np.ones((trial_num_train['left']))*evnet_dict_marker['left'],np.ones((trial_num_train['right']))*evnet_dict_marker['right']),axis = 0)
    
    # use mutual infomation rank
    mutual_info = feature_selection.mutual_info_classif(X,y)
    mutual_info_rank = np.argsort(mutual_info)[::-1]
    mutual_info_rank_use = mutual_info_rank[:k];
    
    # use mrmr
    # yy = np.expand_dims(y, axis=1)
    # ar_xy = np.concatenate((yy,X),axis = 1)
    # name_list = [str(x) for x in range(X.shape[1])] 
    # name_list.insert(0,'class')
    # df_data = pd.DataFrame(ar_xy,columns = name_list)
    # sel_features_idx_str = pymrmr.mRMR(df_data, 'MID', k)
    # sel_features_idx = np.array([int(x) for x in sel_features_idx_str])
    
    #if do not use mrmr, just common this line
    # mutual_info_rank_use = sel_features_idx
    
    X_train_mutual_info = X[:,mutual_info_rank_use]    
    
    # clf = make_pipeline(StandardScaler(), SVC(gamma='auto'))
    # clf.fit(X_train_mutual_info, y)
    # Pipeline(steps=[('standardscaler', StandardScaler()),
    #                 ('svc', SVC(gamma='auto'))])
    
    # clf = SVC(random_state=42)
    # clf.fit(X_train_mutual_info,y)
    
    std = StandardScaler()
    X_train_mutual_info_std = std.fit_transform(X_train_mutual_info)
    
    
    #%%
            
    X_test = np.array([]).reshape((trial_num_test['left']+trial_num_test['right']),0)
    
    # test_trial_numbers[cl]
    for band_key, trials in trials_all.items(): 
    
        trials_test={}
        for cl in cl_lab:   
            trials_test[cl] = trials[cl][:,:,trial_num_train[cl]:] # note here is :  trial_num_train[cl]: means the test trials
           
        mW = []
        trials_csp={}
        
        trials_csp_cl1 = mcspx.apply_csp(mW_all_bands[band_key], trials_test['left'])
        trials_csp_cl2 = mcspx.apply_csp(mW_all_bands[band_key], trials_test['right'])
        
        trials_csp = {'left': trials_csp_cl1,'right': trials_csp_cl2}
    
        # plot the figures
        # nsamples_win = len(np.arange(int(signal_win_start*fs), int(signal_win_end*fs)))
        # mplt = plotsomex(nchannels, nsamples_win, fs)    
        # mplt.plot_psd_simple(trials_csp[cl1],trials_csp['right'])
    
        trials_csp_f={}
        trials_csp_f['left'] = trials_csp['left'][csp_feature_index,:,:]
        trials_csp_f['right'] = trials_csp['right'][csp_feature_index,:,:]
      
        trials_logvar = {'left': np.log(np.var((trials_csp_f['left']), axis=1)),
                        'right': np.log(np.var((trials_csp_f['right']), axis=1))}
    
        x = np.concatenate((trials_logvar['left'].T,trials_logvar['right'].T),axis = 0)    
        
        X_test = np.concatenate((X_test,x),axis = 1)
    
    # apply the mutual info rank we get from the training data
    X_test_mutu_info = X_test[:,mutual_info_rank_use]  
    
    y_test = np.concatenate((np.ones((trial_num_test['left']))*evnet_dict_marker['left'],np.ones((trial_num_test['right']))*evnet_dict_marker['right']),axis = 0)
    
    std = StandardScaler()
    X_test_std = std.fit_transform(X_test_mutu_info)
    
    #%% fit data:
        
        
    params = {
        'C':[0.1,0.5,1,10,100],
        'gamma':['scale',1,0.1,0.001,0.001,0.0001],
        'kernel':['rbf','linear', 'poly','sigmoid']
        }
    
    # optimal_params = GridSearchCV(SVC(), param_grid=params, cv=5)
    optimal_params = GridSearchCV(SVC(),param_grid=params,cv=5)
    
    optimal_params.fit(X_train_mutual_info_std, y)
    
    print('best paras: ',optimal_params.best_estimator_)
    print('best score: ',optimal_params.best_score_)
    

    # cut 
    # grid_predictions = optimal_params.predict(X_test_std)
    # print(classification_report(y_test, grid_predictions))
    
    
    # clf = SVC(C=optimal_params.best_params_['C'],
    #           gamma=optimal_params.best_params_['gamma'],
    #           kernel=optimal_params.best_params_['kernel'],
    #           random_state=42)
    # # clf = SVC(C=0.1,
    # #            kernel='sigmoid',
    # #            random_state=42)
    # # clf = SVC()
    
    
    # clf.fit(X_train_mutual_info,y)
    
    # r=clf.predict(X_test_std)
    
    # # print('predict label:'+str(r))
    # # right_label = np.concatenate((np.ones(trial_num_test['left'])*evnet_dict_marker['left'], np.ones(trial_num_test['right'])*evnet_dict_marker['right'])) 
    # # print('real    label:'+str(right_label))
    
    # #%%
    # # Print confusion matrix
    # conf = np.array([
    #     [(r[0:trial_num_test['left']] == evnet_dict_marker['left']).sum(), (r[trial_num_test['left']:] == evnet_dict_marker['left']).sum()],
    #     [(r[0:trial_num_test['left']] == evnet_dict_marker['right']).sum(), (r[trial_num_test['left']:] == evnet_dict_marker['right']).sum()],
    # ])
    
    
    # print('Confusion matrix:')
    # print(conf)
    # print()
    # print('Accuracy: %.3f' % (np.sum(np.diag(conf)) / float(np.sum(conf))))   

    #%%
if __name__ == '__main__':

    calculate_model()
    # plt.show (block=True)

