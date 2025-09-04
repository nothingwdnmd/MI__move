# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 15:47:15 2023

@author: xiaok
"""

import json
import numpy as np
from sin_signal import SinSignalx 

example_cmd_str = '{"mac":"d5:5:82:f0:1e:a","chn":"8","pkn":756,\
"eeg":[0,0,0,0,0,0,65535,65535,65535,65535,65535,65535,65535,65535,\
0,0,0,0,0,0,0,0,0,0,0,0,65535,65535,65535,65535,65535,65535,65535,\
65535,65535,0,0,0,0,0,0,0,0,0,0,0,0,65535,65535,65535,65535,65535,\
65535,65535,65535,65535,0,0,0,0,0,0,0,0,0,0,0,41120,65535,65535,\
65535,65535,65535,65535,65535,65535,30101,0,0,0],"acc":[67,-10,638,-345]}'
    
class SignalGeneratorJsonx(object):
    """docstring for SignalGeneratorJsonx"""
    def __init__(self):
        super(SignalGeneratorJsonx, self).__init__()
        self.ch_n = 8 #channel number

        # set the signals to these channels 
        """
        SinSignalx(freq,signal_amp,noise_amp)
        Parameters
        freq : the frequency of the signal        
        signal_amp: the amplitude of the signal
        noise_amp:the amplitude of the noise
        """
# +SinSignalx(15,10,0.2)
        channel_1 = SinSignalx(4,5,0.8)+SinSignalx(15,10,0.2)
        channel_2 = SinSignalx(5,15,0)
        channel_3 = SinSignalx(8,5,0.4)+SinSignalx(21,8,4)
        channel_4 = SinSignalx(10,7,90)
        channel_5 = SinSignalx(12,20,1.2)
        channel_6 = SinSignalx(14,50,3.8)
        channel_7 = SinSignalx(16,3,0.8)
        channel_8 = SinSignalx(18,30,0.8)

        self.ss_s = {}
        for i in range(8):
            self.ss_s[i]=vars()["channel_"+str(i+1)]

        self.json_data_template = json.loads(example_cmd_str)

    def get_json_array(self):
        s_tmp = np.empty(shape=(10,0))
        for i in range(8):
            tmp = self.ss_s[i].get_data_points(10)
            s_tmp = np.column_stack((s_tmp, tmp))
            

        ss = np.reshape(s_tmp, (80))*5
        # print(ss[:10])
        # ss_int = int(ss)
        ss_int = ss.astype(int)+32768
        # print(ss_int[:10])
        json_data = self.json_data_template
        json_data["eeg"]=ss_int.tolist()
        return json.dumps(json_data)
