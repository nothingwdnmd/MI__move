# -*- coding: utf-8 -*-
import numpy as np
from pathlib import Path
from datetime import datetime
import pyedflib
import debugPrinter as dp

class FileNameGenerator(object):
    def __init__(self, path_str_root):
        super(FileNameGenerator, self).__init__()
        self.fileNameCounter = 0
        self.path_str_root = path_str_root

    def generate_name(self):
        now = datetime.now()
        str_dateTime = now.strftime("%m%d%H%M")# %S
        path_str = self.path_str_root+"/"+str_dateTime
        if Path(path_str).exists():
            num = 1
            path_str_origin = path_str
            path_str = path_str_origin +"("+str(num)+")"
            while Path(path_str).exists():
                num = num+1
                path_str = path_str_origin+"("+str(num)+")"

        return path_str

    def get_file_name(self,path_str):
        txtName=self.fileName_first_letter+str(self.fileNameCounter)+self.extended_str
        self.fileNameCounter = self.fileNameCounter+1
        filePathName = path_str+"/"+txtName
        return filePathName

class EDFSaver(object):
    """docstring for FileSaver"""
    def __init__(self, path_str):
        super(EDFSaver, self).__init__()
        self.fng = FileNameGenerator(path_str)
        self.path_str = None
        self.data = None
        self.data_1ch = None
        self.data_acc=None
        self.channel_info = []
        self.channel_info_1ch = []

        # self.data_list = []
        self.save_on = 0
        self.f=None
        self.fs_eeg = 128
        self.ch_8_1 = True #use 8 channels or 1 channel
        self.filePathName = ''

    def use_one_channel(self):
        self.ch_8_1 = False #use 1 channel

    def use_eight_channels(self):
        self.ch_8_1 = True #use 8 channels 

    def make_path(self,path_str):
        if Path(path_str).exists():
            return 1

        Path(path_str).mkdir()
        self.path_str = path_str

        return 0

    def get_name(self):
        return self.fng.generate_name()

    def new_data(self,s,ts,d):
        if (self.save_on):
            t = np.expand_dims(ts, axis=1)
            dd = np.hstack((t,d))
            if(s=='eeg'):
                self.data = np.concatenate((self.data,dd), axis=0)
            if(s=='acc'):
                self.data_acc = np.concatenate((self.data_acc,dd), axis=0)
            if(s=='mar'):
                self.data_marker = np.concatenate((self.data_marker,dd), axis=0)

    def new_data_1ch(self,s,ts,d):
        if (self.save_on):
            t = np.expand_dims(ts, axis=1)
            dd = np.hstack((t,d))
            if(s=='eeg'):
                self.data_1ch = np.concatenate((self.data_1ch,dd), axis=0)
            if(s=='mar'):
                self.data_marker = np.concatenate((self.data_marker,dd), axis=0)

    def setup(self,file_path_str,file_name_str):
        # ch_dict = {'label': 'lslts', 'dimension': 'ms', 'sample_frequency': 128}
        # self.channel_info.append(ch_dict)
        
        ch_dict = {'label': 'F4', 'dimension': 'uV', 'sample_frequency': 128,'physical_max': 6553.6, 'physical_min': -6553.6, 
            'digital_max': 32767, 'digital_min': -32768, 'transducer': '', 'prefilter':''}
        self.channel_info.append(ch_dict)
        ch_dict = {'label': 'C4', 'dimension': 'uV', 'sample_frequency': 128,'physical_max': 6553.6, 'physical_min': -6553.6, 
            'digital_max': 32767, 'digital_min': -32768, 'transducer': '', 'prefilter':''}
        self.channel_info.append(ch_dict)
        ch_dict = {'label': 'P4', 'dimension': 'uV', 'sample_frequency': 128,'physical_max': 6553.6, 'physical_min': -6553.6, 
            'digital_max': 32767, 'digital_min': -32768, 'transducer': '', 'prefilter':''}
        self.channel_info.append(ch_dict)
        ch_dict = {'label': 'Fz', 'dimension': 'uV', 'sample_frequency': 128,'physical_max': 6553.6, 'physical_min': -6553.6, 
            'digital_max': 32767, 'digital_min': -32768, 'transducer': '', 'prefilter':''}
        self.channel_info.append(ch_dict)
        ch_dict = {'label': 'Cz', 'dimension': 'uV', 'sample_frequency': 128,'physical_max': 6553.6, 'physical_min': -6553.6, 
            'digital_max': 32767, 'digital_min': -32768, 'transducer': '', 'prefilter':''}
        self.channel_info.append(ch_dict)
        ch_dict = {'label': 'F3', 'dimension': 'uV', 'sample_frequency': 128,'physical_max': 6553.6, 'physical_min': -6553.6, 
            'digital_max': 32767, 'digital_min': -32768, 'transducer': '', 'prefilter':''}
        self.channel_info.append(ch_dict)
        ch_dict = {'label': 'C3', 'dimension': 'uV', 'sample_frequency': 128,'physical_max': 6553.6, 'physical_min': -6553.6, 
            'digital_max': 32767, 'digital_min': -32768, 'transducer': '', 'prefilter':''}
        self.channel_info.append(ch_dict)
        ch_dict = {'label': 'P3', 'dimension': 'uV', 'sample_frequency': 128,'physical_max': 6553.6, 'physical_min': -6553.6, 
            'digital_max': 32767, 'digital_min': -32768, 'transducer': '', 'prefilter':''}
        self.channel_info.append(ch_dict)

        ch_dict = {'label': 'Fp1', 'dimension': 'uV', 'sample_frequency': 128,'physical_max': 6553.6, 'physical_min': -6553.6, 
            'digital_max': 32767, 'digital_min': -32768, 'transducer': '', 'prefilter':''}
        self.channel_info_1ch.append(ch_dict)

        self.data = np.empty(shape=(0,9))
        self.data_1ch = np.empty(shape=(0,2))

        self.data_acc = np.empty(shape=(0,5))
        self.data_marker = np.empty(shape=(0,2))

        self.filePathName = file_path_str+'/'+file_name_str+'_.edf'

        self.save_on = 1
        
    def flush_data(self):

        if (self.ch_8_1):
            self.f = pyedflib.EdfWriter(self.filePathName, 8,file_type=pyedflib.FILETYPE_EDFPLUS)
            self.f.setSignalHeaders(self.channel_info)
        else :            
            self.f = pyedflib.EdfWriter(self.filePathName, 1,file_type=pyedflib.FILETYPE_EDFPLUS)
            self.f.setSignalHeaders(self.channel_info_1ch)


############################ eeg data
        data_save=None
        if (self.ch_8_1):
            data_save = self.data.copy()
        else :            
            data_save = self.data_1ch.copy()

        # print(data_save.shape)

        t_arr = data_save[:,0]
        data_save = data_save.astype(np.int32)
        data_save = data_save - 32768

        data_list=[]
        for i in range(data_save.shape[1]-1):
            tmp = data_save[:,i+1].copy()
            data_list.append(tmp)

############################ marker data

        m_arr = self.data_marker[:,0]

        m_index = np.searchsorted(t_arr, m_arr)

        m_t = m_index/self.fs_eeg 

        # for m in m_t:
        #     self.f.writeAnnotation(m, -1, str(v))
        for i, m in enumerate(m_t):
            self.f.writeAnnotation(m, -1, str(self.data_marker[i,1]))

############################ save

        self.f.writeSamples(data_list,digital=True)
        self.f.close()
        print('data saved')
        # del self.f




