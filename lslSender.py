# -*- coding: utf-8 -*-
# from collections import deque

import pylsl

class LSLSender(object):
    """docstring for DataPrc"""
    def __init__(self, arg):
        super(LSLSender, self).__init__()
        self.arg = arg
        info_eeg = pylsl.stream_info('mi_eeg','eeg',8,128,pylsl.cf_int32,'mi')
        self.outlet_eeg = pylsl.stream_outlet(info_eeg)

        info_acc = pylsl.stream_info('mi_acc','acc',4,12.8,pylsl.cf_float32,'mi')
        self.outlet_acc = pylsl.stream_outlet(info_acc)

        info_eeg_hb = pylsl.stream_info('hb_eeg','eeg',1,128,pylsl.cf_int32,'hb')
        self.outlet_eeg_hb = pylsl.stream_outlet(info_eeg_hb)

    def send_eeg(self,e):
        mysample = pylsl.vectorf(e)
        self.outlet_eeg.push_sample(mysample)

    def send_acc(self,a):
        mysample = pylsl.vectorf(a)
        self.outlet_acc.push_sample(mysample)

    def send_eeg_hb(self,e):
        mysample = pylsl.vectorf(e)
        self.outlet_eeg_hb.push_sample(e)













