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
import mne
import os
import json
from bandpassx import BANDPASSx as bandpassx
from calcspx import CALCSPx as calcspx

class CurCtrlClassifier(object):
	"""docstring for CurCtrlCalculator"""
	def __init__(self,ch_num,fs):
		super(CurCtrlClassifier,self).__init__()
		self.do_calculate = 0 # 0 is idle, 1 means do predict
		self.ch_num = ch_num
		self.fs = fs
		self.data = np.empty(shape=(self.fs,self.ch_num)) 
		# fs+1 because the training data in the program use the data fs+1, i.e.129 samples

		self.data_counter = 0

		self.model = None
		self.mcspx = calcspx()
		self.confidence_thr_75 = 0.75
		self.confidence_thr_70 = 0.7
		self.confidence_thr_65 = 0.65

		id_num = random.randint(1, 10000)
		name_str = 'curctrl_marker_'+str(id_num)
		info = pylsl.stream_info(name = name_str, type='Markers', channel_count=1,channel_format='int32', source_id='curctrl_marker_1')
		self.outlet = pylsl.stream_outlet(info)  

		with open('task_markers.json', 'r') as file:
			self.task_markers = json.load(file)

	def open_calculate(self):
		self.do_calculate = 1 

	def close_calculate(self):
		self.do_calculate = 0 

	def load_model(self,fileName):
		train_model = pickle.load(open(fileName,'rb'))
		self.clf = train_model['clf'] 
		self.mW_all_bands = train_model['csp']
		self.mutual_info_rank_use = train_model['mu_inf']
		self.filter_bands_str_num = train_model['filter_bands']
		self.csp_feature_index = train_model['csp_feature_index']
		self.std = train_model['std']

	def new_data(self,d):
		if self.do_calculate == 1:
			sample_num = d.shape[0]
			# dp.dpt(d[0][1])
			dd = (d-32768)/5000000
			# dp.dpt(dd[0][1])

			self.data = np.concatenate((self.data[sample_num:,:],dd), axis=0)
			self.data_counter = self.data_counter+sample_num
			if self.data_counter>6:
				self.data_counter=0
				if (self.clf is not None):
					eeg_pred = self.data
					eeg_pred = np.transpose(eeg_pred)
					# dp.dpt(eeg_pred.shape)

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

					# print('---------$$$$$$$$$$$--------- ')
					# print(X_test.shape)

					X_test_mutu_info = X_test[self.mutual_info_rank_use]  

					# print('---------$$$$$$$$$$$--------- ')
					# print(X_test_mutu_info.shape)
					X_test_mutu_info = X_test_mutu_info.reshape(-1,1)
					X_test_mutu_info = X_test_mutu_info.T

					# print('---------$$$$$$$$$$$--------- ')
					# print(X_test_mutu_info.shape)

					X_test_std = self.std.transform(X_test_mutu_info)
					# print(X_test_std)
					# r=self.clf.predict(X_test_std.T)

					r_proba=self.clf.predict_proba(X_test_std)
					r_proba = r_proba.squeeze()
					# dp.dpt(r_proba)
					# print(r_proba[0])

					# print(r_proba[1])
					# print(max(r_proba))


					if r_proba[0]<r_proba[1]:
						if max(r_proba)<self.confidence_thr_75:
							return
						self.outlet.push_sample(self.task_markers['mu_rhythm_low'])
						print('up')
					else:
						if max(r_proba)<self.confidence_thr_70:
							return
						self.outlet.push_sample(self.task_markers['mu_rhythm_high'])
						print('down')

					# if r[0]==self.task_markers['curctrl_down'][0]:
					# 	print('down')
					# 	self.outlet.push_sample(self.task_markers['mu_rhythm_high'])
					# if r[0]==self.task_markers['curctrl_up'][0]:
					# 	self.outlet.push_sample(self.task_markers['mu_rhythm_low'])
					# 	print('up')


