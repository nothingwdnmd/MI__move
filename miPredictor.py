# -*- coding: utf-8 -*-
import numpy as np
import json
import pickle
import random
import pylsl
import debugPrinter as dp
from calcspx import CALCSPx as calcspx

from plotsome import PLOTSOMEx as plotsomex

import pandas as pd

from sklearn import feature_selection

from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

import pickle

from mne.io import concatenate_raws, read_raw_edf

from bandpassx import BANDPASSx as bandpassx
from calcspx import CALCSPx as calcspx

class MIPredictor(object):
	"""docstring for MIPredictor"""
	def __init__(self,ch_num):
		super(MIPredictor,self).__init__()
		self.do_predict = 0 # 0 is idle, 1 means do predict
		self.ch_num = ch_num
		self.model = None
		self.data = np.empty(shape=(0,self.ch_num))
		self.mcspx = calcspx()


		id_num = random.randint(1, 10000)
		name_str = 'predict_marker_'+str(id_num)
		info = pylsl.stream_info(name = name_str, type='Markers', channel_count=1,channel_format='int32', source_id='predict_marker_1')
		self.outlet = pylsl.stream_outlet(info)  

		# self.model_path_name = './models/'+fileName

		with open('task_markers.json', 'r') as file:
			self.task_markers = json.load(file)

	def load_model(self,fileName):
		# self.model_path_name = './models/'+fileName
		train_model = pickle.load(open(fileName,'rb'))
		self.clf = train_model['clf'] 
		self.mW_all_bands = train_model['csp']
		self.mutual_info_rank_use = train_model['mu_inf']
		self.filter_bands_str_num = train_model['filter_bands']
		self.csp_feature_index = train_model['csp_feature_index']
		self.std = train_model['std']
		self.fs = 128


	def open_predict(self):
		self.do_predict = 1 

	def close_predict(self):
		self.do_predict = 0 

	def new_data(self,d):
		if self.do_predict == 1:
			self.data = np.concatenate((self.data,d), axis=0)

	def new_marker(self,d):
		if self.do_predict == 1:
			if d[0] == self.task_markers['mi_end']:
				dp.dpt(self.data.shape)
				dp.dpt('predicting ... ')
				if (self.clf is not None):
					cut_begin = round(128*2.5)
					cut_end = round(128*0.5)
					if self.data.shape[0]<cut_begin:
						return
					eeg_pred = self.data[-cut_begin:-cut_end,:]
					eeg_pred = np.transpose(eeg_pred)

					eeg_filterd = {}    
					for band_str, band_list in self.filter_bands_str_num.items(): 
						lo, hi = band_list    
						mbandpassx = bandpassx(self.fs, lo, hi)
						eeg_filterd[band_str] = mbandpassx.apply_filter_2d(eeg_pred)

					X_test = np.array([]).reshape(0,)
					for band_key, trial in eeg_filterd.items():
						trial_csp = self.mcspx.apply_csp_single_trial(self.mW_all_bands[band_key], trial)

						trial_csp_f = trial_csp[self.csp_feature_index,:]
						trials_logvar = np.log(np.var(trial_csp_f, axis=1))

						X_test = np.concatenate((X_test,trials_logvar),axis = 0)

					X_test_mutu_info = X_test[self.mutual_info_rank_use]  
					X_test_mutu_info = X_test_mutu_info.reshape(-1,1)
					X_test_std = self.std.fit_transform(X_test_mutu_info)
					# print(X_test_std)
					r=self.clf.predict(X_test_std.T)

					dp.dpt(r)

					if r[0]==self.task_markers['left'][0]:
						self.outlet.push_sample(self.task_markers['predict_left'])
					if r[0]==self.task_markers['right'][0]:
						self.outlet.push_sample(self.task_markers['predict_right'])

				self.data = np.empty(shape=(0,self.ch_num))



