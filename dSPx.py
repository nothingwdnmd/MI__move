# -*- coding: utf-8 -*-
from filterButter import FilterButter
import numpy as np


class DSPx(object):
	"""docstring for DSPx"""
	def __init__(self,ch_num):
		super(DSPx, self).__init__()
		# self.hp_p3 = FilterButter(128,3,0.3,'high')
		# self.lp_40 = FilterButter(128,3,40,'low')
		self.hp_p3 = []
		self.lp_40 = []
		for i in range(ch_num):
			self.hp_p3.append(FilterButter(128,3,0.3,'high'))
			self.lp_40.append(FilterButter(128,3,40,'low'))

	def filter_dummy(self,arr):
		return arr

	def filter(self,arr):
		# arr should be 2 dimensional array, for example shape = (6,8), means 8 channels, 6 time points
		filtered_data = np.zeros(shape=(arr.shape))
		for i in range(arr.shape[0]):
			tmp = arr[i,:]
			filtered_data_one_time_point = self.filter_arr(tmp)
			filtered_data[i,:]=filtered_data_one_time_point

		return filtered_data

	def filter_arr(self,arr):
		# arr should be 1 dimensional array
		# print(arr.shape)
		tmp = np.zeros(shape=(arr.shape))

		for i,a in enumerate(arr):
			# t = self.lp_40.filter(a)
			# t = self.hp_p3.filter(t)
			# tmp[i] = t

			tmp[i] = self.hp_p3[i].filter(self.lp_40[i].filter(a))

		return tmp




