# -*- coding: utf-8 -*-
from collections import deque

from scipy import signal

class FilterButter(object):
	"""docstring for FilterButter"""
	def __init__(self,fs,order,fc,s): #s is 'high' or 'low' or ...
		super(FilterButter, self).__init__()
		self.fs = fs
		self.order = order
		self.b, self.a = signal.butter(order, fc/(fs/2), s)
		self.arr_len = order+1

		self.x = deque(self.arr_len*[0.0],self.arr_len)
		self.y = deque(self.arr_len*[0.0],self.arr_len)

	def filter_dummy(self,f):
		return f

	def filter(self,f):
		self.x.append(f)
		tmp = 0
		for i in range(self.arr_len):
			t = self.b[i]*self.x[self.arr_len-1-i]
			tmp = t+tmp

		for i in range(self.arr_len-1):
			t = -self.a[i+1]*self.y[self.arr_len-1-i]
			tmp = t+tmp
		
		self.y.append(tmp)
		return tmp

	# def filter(self,f,a,b):
			
	# 		tmp= b[0]*self.x[3] \
	# 			+b[1]*self.x[2] \
	# 			+b[2]*self.x[1] \
	# 			+b[3]*self.x[0] \
	# 			-a[0]*self.y[3] \
	# 			-a[1]*self.y[2] \
	# 			-a[2]*self.y[1]
	# 		self.y.append(tmp)
	# 		return tmp




