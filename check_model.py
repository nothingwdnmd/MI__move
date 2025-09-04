# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
    
from bandpassx import BANDPASSx as bandpassx

from calcspx import CALCSPx as calcspx
import pickle

import mne
import json

import matplotlib.pyplot as plt
from plotsome import PLOTSOMEx as plotsomex
import pandas as pd
from sklearn import feature_selection
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from mne.io import concatenate_raws, read_raw_edf


# ModelFileName = './models/new_model_bv8#p!_.mim'
ModelFileName = './models/new_model_bv8#p!_.mim'

test_data_file_name = './data/08021021_image_move/08021021_image_move_.edf'
test_data_file_name = './data/08041210_mi/08041210_mi_.edf'
test_data_file_name = './data/08041214_mi/08041214_mi_.edf'

with open('task_markers.json', 'r') as file:
    markers = json.load(file)
    
# cl_lab = ['left','right']

label_left_int = markers['left'][0]
label_right_int = markers['right'][0]

#%%

train_model = pickle.load(open(ModelFileName,'rb'))
clf = train_model['clf'] 
mW_all_bands = train_model['csp']
mutual_info_rank_use = train_model['mu_inf']
filter_bands_str_num = train_model['filter_bands']


raw=read_raw_edf(test_data_file_name,preload=False)
events_from_annot,event_dict = mne.events_from_annotations(raw)
raw_data = raw.get_data()

key_list = list(event_dict.keys())
val_list = list(event_dict.values())

events_marker = events_from_annot.copy()

for i, c in enumerate(events_from_annot[:,2]):
    tmp = key_list[val_list.index(c)]
    tmp = int(float(tmp))
    events_marker[i,2]=tmp

events_marker = np.delete(events_marker,np.where((events_marker[:,2]!=label_left_int) & (events_marker[:,2]!=label_right_int))[0],0)

evnet_dict_marker = {
    'left':label_left_int,
    'right':label_right_int    
}

# fig = mne.viz.plot_events(
#     events_marker, event_id=evnet_dict_marker, sfreq=raw.info["sfreq"], first_samp=raw.first_samp
# )

epochs = mne.Epochs(
    raw,
    events_marker,
    event_id=evnet_dict_marker,
    tmin=0.5,
    tmax=2.5,
    baseline = None
)

trials_right = epochs["right"].get_data()
trials_left = epochs["left"].get_data()

fs = 128
mcspx = calcspx()
csp_feature_index = np.array([0,1,2,-3,-2,-1])

r_left = np.zeros(shape = (trials_left.shape[0],))

for i in range(trials_left.shape[0]):
         
    tmp = trials_left[i,:,:]
    nsamples,nchannels = tmp.shape      
    
    eeg_filterd = {}    
    for band_str, band_list in filter_bands_str_num.items(): 
        # print('Filtering through '+band_str+' Hz band')
        lo, hi = band_list    
        mbandpassx = bandpassx(fs, nchannels, nsamples, lo, hi)
        eeg_filterd[band_str] = mbandpassx.apply_filter_2d(tmp)
    
    X_test = np.array([]).reshape(1,0)
    
    for band_key, band_data in eeg_filterd.items():         
      
        trials_csp = mcspx.apply_csp_single_trial(mW_all_bands[band_key], band_data)
    
        trials_csp_f={}
        trials_csp_f = trials_csp[csp_feature_index,:]
      
        trials_logvar = np.log(np.var((trials_csp_f), axis=1))
        x = np.expand_dims(trials_logvar, axis=1).T        
        X_test = np.concatenate((X_test,x),axis = 1)    
    
    # apply the mutual info rank we get from the training data
    X_test = X_test[:,mutual_info_rank_use]  
    
    r_left[i]=clf.predict(X_test)
        
    
    
r_right = np.zeros(shape = (trials_right.shape[0],))
for i in range(trials_right.shape[0]):
         
    tmp = trials_right[i,:,:]
    nsamples,nchannels = tmp.shape      
    
    eeg_filterd = {}    
    for band_str, band_list in filter_bands_str_num.items(): 
        # print('Filtering through '+band_str+' Hz band')
        lo, hi = band_list    
        mbandpassx = bandpassx(fs, nchannels, nsamples, lo, hi)
        eeg_filterd[band_str] = mbandpassx.apply_filter_2d(tmp)
    
    X_test = np.array([]).reshape(1,0)
    
    for band_key, band_data in eeg_filterd.items():         
      
        trials_csp = mcspx.apply_csp_single_trial(mW_all_bands[band_key], band_data)
    
        trials_csp_f={}
        trials_csp_f = trials_csp[csp_feature_index,:]
      
        trials_logvar = np.log(np.var((trials_csp_f), axis=1))
        x = np.expand_dims(trials_logvar, axis=1).T        
        X_test = np.concatenate((X_test,x),axis = 1)    
    
    # apply the mutual info rank we get from the training data
    X_test = X_test[:,mutual_info_rank_use]  
    
    r_right[i] = clf.predict(X_test)
    
r_all = np.concatenate((np.expand_dims(r_left, axis=1), np.expand_dims(r_right, axis=1)),axis=1)

#  not completed