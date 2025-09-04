# -*- coding: utf-8 -*-
"""
Created on Tue May  2 11:38:24 2023

@author: xiaok

# **References:**   
# 
# [1] Kai Keng Ang, Zheng Yang Chin, Haihong Zhang and Cuntai Guan, "Filter Bank Common Spatial Pattern (FBCSP) in Brain-Computer Interface," 2008 IEEE International Joint Conference on Neural Networks (IEEE World Congress on Computational Intelligence), Hong Kong, 2008, pp. 2390-2397, doi: 10.1109/IJCNN.2008.4634130.    
# [2] Ang, K. K., Chin, Z. Y., Wang, C., Guan, C., & Zhang, H. (2012). Filter Bank Common Spatial Pattern Algorithm on BCI Competition IV Datasets 2a and 2b. Frontiers in Neuroscience, 6. doi: 10.3389/fnins.2012.00039

* Thanks to Dr. Marijn van Vliet, https://github.com/wmvanvliet/neuroscience_tutorials/tree/master/eeg-bci

"""
# In[1]:


import numpy as np
import scipy.io
import matplotlib.pyplot as plt
    
import scipy.signal 

from bandpassx import BANDPASSx as bandpassx
from calcspx import CALCSPx as calcspx

from plotsome import PLOTSOMEx as plotsomex

import pandas as pd

from sklearn import feature_selection

from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from mne.io import concatenate_raws, read_raw_edf
import mne
# import pymrmr



# In[2]:


# plt.close('all')

dframe = pd.DataFrame
    
percentage_train_test = 0.7
signal_win_start = 0.5 #second
signal_win_end = 2.5 #second

# 6 filters (i.e., 3 pairs), corresponding to the 3 largest and 3 lowest of csp
feature_index = np.array([0,1,2,-3,-2,-1])

# pairs of CSP features selected in mutual info
k=6

#%% my mi data
use_my_data = 0
    
if use_my_data == 1:

    raw=read_raw_edf("./data/08041210_mi/08041210_mi_.edf",preload=False)
    raw=read_raw_edf("./data/08041214_mi/08041214_mi_.edf",preload=False)
    raw=read_raw_edf("./training_data/08151321_mi_02_.edf",preload=False)

    raw_eeg = raw.get_data()
    fs = raw.info['sfreq']
    events_from_annot,event_dict = mne.events_from_annotations(raw)

    key_list = list(event_dict.keys())
    val_list = list(event_dict.values())

    event_codes_precursor = list()
    event_onset_precursor = list()

    for i, c in enumerate(events_from_annot[:,2]):
        tmp = key_list[val_list.index(c)]
        tmp = int(float(tmp))
        if tmp == 1 or tmp == 2:
            event_codes_precursor.append(tmp)
            event_onset_precursor.append(events_from_annot[i,0])       

    tmp = [-1 if i == 2 else i for i in event_codes_precursor]
    event_codes_ = np.expand_dims(tmp,axis=0)
    event_codes = event_codes_.astype('int16')
    event_onsets = np.expand_dims(event_onset_precursor,axis=0)
    cl_lab = ['left','right']

# what the above does is to make the exactly same variable with the data from BCICIV dataset 

##%%  BCICIV dataset     

else:

    fileName = './competition_dataset/BCICIV_1_mat/BCICIV_calib_ds1a.mat'
    fileName = './competition_dataset/BCICIV_1_mat/BCICIV_calib_ds1b.mat'
    fileName = './competition_dataset/BCICIV_1_mat/BCICIV_calib_ds1c.mat'
    fileName = './competition_dataset/BCICIV_1_mat/BCICIV_calib_ds1d.mat'
    fileName = './competition_dataset/BCICIV_1_mat/BCICIV_calib_ds1e.mat'
    fileName = './competition_dataset/BCICIV_1_mat/BCICIV_calib_ds1f.mat'
    fileName = './competition_dataset/BCICIV_1_mat/BCICIV_calib_ds1g.mat'
    
    m = scipy.io.loadmat(fileName, struct_as_record=True)

    fs = m['nfo']['fs'][0][0][0][0]
    raw_eeg = m['cnt'].T

    event_onsets = m['mrk'][0][0][0]
    event_codes = m['mrk'][0][0][1]

    cl_lab = [s[0] for s in m['nfo']['classes'][0][0][0]]
    

nchannels, nsamples = raw_eeg.shape

cl1 = cl_lab[0]
cl2 = cl_lab[1]      

train_event_onsets_len = round(event_onsets.shape[1]*percentage_train_test)
train_event_codes_len = round(event_codes.shape[1]*percentage_train_test)

event_onsets_train = event_onsets[:,:train_event_onsets_len]
event_codes_train = event_codes[:,:train_event_codes_len]

ntrials_trian = {}
for cl, code in zip(cl_lab, np.unique(event_codes_train)):   
    ntrials_trian[cl]= np.sum(event_codes_train == code)


event_onsets_test = event_onsets[:,train_event_onsets_len:]
event_codes_test = event_codes[:,train_event_codes_len:]   

ntrials_test = {}
for cl, code in zip(cl_lab, np.unique(event_codes_test)):   
    ntrials_test[cl]= np.sum(event_codes_test == code)

unsigned_label_cl1 = 1
unsigned_label_cl2 = 2


# filter bank:
# 1. 4-8Hz
# 2. 8-12Hz
# 3. 12-16Hz
# 4. 16-20Hz
# 5. 20-24Hz
# 6. 24-28Hz
# 7. 28-32Hz
band_interval = 4
filter_band = np.arange(4, 32, step = band_interval)
filter_bands_str_num={}

for band_lo in filter_band:
    # This will be new key inside the EEG_filtered
    lo = band_lo
    hi = band_lo+band_interval
    band = "{:02d}_{:02d}".format(lo,hi)    
    print(': {} Hz'.format(band))
    filter_bands_str_num[band]=[lo,hi]


eeg_filterd = {}

for band_str, band_list in filter_bands_str_num.items(): 
    print('Filtering through '+band_str+' Hz band')
    lo, hi = band_list    
    mbandpassx48 = bandpassx(fs, lo, hi)
    eeg_filterd[band_str] = mbandpassx48.apply_filter_2d(raw_eeg)


def epoch_eeg_data(data,event_onsets,event_codes,start_time,end_time,fs):
    trials = {}    
    win = np.arange(int(start_time*fs), int(end_time*fs))
    nsamples = len(win)
    for cl, code in zip(cl_lab, np.unique(event_codes)):    
        cl_onsets = event_onsets[event_codes == code]    
        trials[cl] = np.zeros((nchannels, nsamples, len(cl_onsets)))    
        for i, onset in enumerate(cl_onsets):
            trials[cl][:,:,i] = data[:, win+onset]
    return trials


X = np.array([]).reshape(event_onsets_train.size,0)
mW_all_bands = {}


for band_key, band_data in eeg_filterd.items(): 
    trials = epoch_eeg_data(band_data,event_onsets_train,event_codes_train,signal_win_start,signal_win_end,fs)

    mcspx = calcspx()
    # [trials_csp_cl1,trials_csp_cl2] = mcspx.get_apply_csp(trials[cl1], trials[cl2])
    mW = mcspx.get_csp_w(trials[cl1], trials[cl2])
    mW_all_bands[band_key] = mW
    trials_csp_cl1 = mcspx.apply_csp(mW, trials[cl1])
    trials_csp_cl2 = mcspx.apply_csp(mW, trials[cl2])
    trials_csp = {cl1: trials_csp_cl1,cl2: trials_csp_cl2}

    # plot the figures
    # nsamples_win = len(np.arange(int(signal_win_start*fs), int(signal_win_end*fs)))
    # mplt = plotsomex(nchannels, nsamples_win, fs)    
    # mplt.plot_psd_simple(trials_csp[cl1],trials_csp[cl2])

    trials_csp_f={}
    trials_csp_f[cl1] = trials_csp[cl1][feature_index,:,:]
    trials_csp_f[cl2] = trials_csp[cl2][feature_index,:,:]
    
        ## check 
    # dframe(trials_csp_f[cl1][:,:,0]).head()
    # dframe(trials_csp[cl1][:,:,0]).head()
    # dframe(trials_csp[cl1][-4:-1,:,0]).head()

    trials_logvar = {cl1: np.log(np.var((trials_csp_f[cl1]), axis=1)),
                     cl2: np.log(np.var((trials_csp_f[cl2]), axis=1))}

    x = np.concatenate((trials_logvar[cl1].T,trials_logvar[cl2].T),axis = 0)
    X = np.concatenate((X,x),axis = 1)


y = np.concatenate((np.ones((ntrials_trian[cl1]))*unsigned_label_cl1,np.ones((ntrials_trian[cl2]))*unsigned_label_cl2),axis = 0)

# use mutual infomation rank
mutual_info = feature_selection.mutual_info_classif(X,y, random_state=0)
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

X_train = X[:,mutual_info_rank_use]


y_test = np.concatenate((np.ones((ntrials_test[cl1]))*unsigned_label_cl1,np.ones((ntrials_test[cl2]))*unsigned_label_cl2),axis = 0)


X_test = np.array([]).reshape(event_onsets_test.size,0)

for band_key, band_data in eeg_filterd.items(): 

    trials = epoch_eeg_data(band_data,event_onsets_test,event_codes_test,signal_win_start,signal_win_end,fs)
    mcspx = calcspx()
    # [trials_csp_cl1,trials_csp_cl2] = mcspx.get_apply_csp(trials[cl1], trials[cl2])

    # # apply the W that we get from training data
    trials_csp_cl1 = mcspx.apply_csp(mW_all_bands[band_key], trials[cl1])
    trials_csp_cl2 = mcspx.apply_csp(mW_all_bands[band_key], trials[cl2])

    trials_csp = {cl1: trials_csp_cl1,cl2: trials_csp_cl2}

    # # plot the figures    
    # nsamples_win = len(np.arange(int(signal_win_start*fs), int(signal_win_end*fs)))
    # mplt = plotsomex(nchannels, nsamples_win, fs)    
    # mplt.plot_psd_simple(trials_csp[cl1],trials_csp[cl2])

    trials_csp_f={}
    trials_csp_f[cl1] = trials_csp[cl1][feature_index,:,:]
    trials_csp_f[cl2] = trials_csp[cl2][feature_index,:,:]

    trials_logvar = {cl1: np.log(np.var((trials_csp_f[cl1]), axis=1)),
                     cl2: np.log(np.var((trials_csp_f[cl2]), axis=1))}

    x = np.concatenate((trials_logvar[cl1].T,trials_logvar[cl2].T),axis = 0)
    X_test = np.concatenate((X_test,x),axis = 1)


# apply the mutual info rank we get from the training data
X_test = X_test[:,mutual_info_rank_use]  


clf = make_pipeline(StandardScaler(), SVC(gamma='auto'))
clf.fit(X_train, y)
Pipeline(steps=[('standardscaler', StandardScaler()),
                ('svc', SVC(gamma='auto'))])

r=clf.predict(X_test)

# std = StandardScaler()
# X_train_std = std.fit_transform(X_train)
# X_test_std = std.fit_transform(X_test)

# clf = SVC(gamma='auto')
# clf.fit(X_train_std,y)
# r=clf.predict(X_test_std)


print(r)
right_label = np.concatenate((np.ones(ntrials_test[cl1])*unsigned_label_cl1, np.ones(ntrials_test[cl2])*unsigned_label_cl2)) 
print(right_label)
    
# Print confusion matrix
conf = np.array([
    [(r[0:ntrials_test[cl1]] == unsigned_label_cl1).sum(), (r[ntrials_test[cl1]:] == unsigned_label_cl1).sum()],
    [(r[0:ntrials_test[cl1]] == unsigned_label_cl2).sum(), (r[ntrials_test[cl1]:] == unsigned_label_cl2).sum()],
])

print('Confusion matrix:')
print(conf)
print()
print('Accuracy: %.3f' % (np.sum(np.diag(conf)) / float(np.sum(conf))))

# plt.show (block=True)